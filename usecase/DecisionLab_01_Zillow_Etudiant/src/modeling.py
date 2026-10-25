"""Prévisions de variation ZHVI ; toutes les métriques sont en points de pourcentage."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from .config import load_config
FEATURES = ['return_1m_pp', 'return_3m_pp', 'return_6m_pp', 'return_12m_pp']
MODELS = ('zero', 'momentum', 'linear')

def features(panel, horizon=6):
    """Entrées à t ; y = 100 * (ZHVI[t+h]/ZHVI[t] - 1). Pas de remplissage temporel."""
    from .validation import validate_panel
    frame = validate_panel(panel)
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError('Horizon entier positif requis.')
    g = frame.groupby('region_id', sort=False)['zhvi']
    for months in [1, 3, 6, 12]:
        frame[f'return_{months}m_pp'] = 100 * (frame.zhvi / g.shift(months) - 1)
    frame['target_pp'] = 100 * (g.shift(-horizon) / frame.zhvi - 1)
    frame['target_end'] = frame.date + pd.offsets.MonthEnd(horizon)
    return frame

def split_training(table, config=None):
    """Purge : toute cible train finit AVANT la première origine de validation."""
    c = config or load_config()
    labeled = table.dropna(subset=FEATURES + ['target_pp']).copy()
    start = pd.Timestamp(c['validation_start'])
    train = labeled.loc[labeled.target_end < start]
    valid = labeled.loc[labeled.date.between(start, pd.Timestamp(c['validation_end']))]
    if train.empty or valid.empty:
        raise ValueError('Train ou validation vide.')
    if train.target_end.max() >= valid.date.min():
        raise ValueError('Chevauchement des cibles train/validation.')
    return train, valid

def fit_predict(train, frame, model_name='linear', horizon=6):
    """Baseline zéro, dernière variation h mois, ou régression linéaire en pipeline."""
    if model_name not in MODELS:
        raise ValueError(f'Modèle inconnu : {model_name}')
    if frame.empty or train.empty:
        raise ValueError('Table vide.')
    if model_name == 'zero':
        return np.zeros(len(frame))
    if model_name == 'momentum':
        feature = f'return_{horizon}m_pp'
        if feature not in frame:
            raise ValueError('Baseline momentum disponible pour h=1,3,6,12.')
        return frame[feature].to_numpy(dtype=float)
    pipe = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(), LinearRegression())
    pipe.fit(train[FEATURES], train.target_pp)
    return pipe.predict(frame[FEATURES])

def metrics(actual, predicted):
    """MAE/RMSE et biais (prédit moins réel), tous en points de pourcentage."""
    if not len(actual) or not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError('Métriques : données absentes ou non finies.')
    return {'mae_pp': float(mean_absolute_error(actual, predicted)),
            'rmse_pp': float(np.sqrt(mean_squared_error(actual, predicted))),
            'bias_pp': float(np.mean(np.asarray(predicted) - np.asarray(actual)))}

def validation_scores(table, config=None):
    c = config or load_config()
    train, val = split_training(table, c)
    return pd.DataFrame([{'model': name, 'observations': len(val), **metrics(
        val.target_pp.to_numpy(), fit_predict(train, val, name, c['horizon_months']))} for name in MODELS])

def decision_predictions(panel, model_name='linear', config=None):
    """Réentraînement avec seulement les labels connus à la date de décision."""
    c = config or load_config()
    cutoff, asof = pd.Timestamp(c['public_cutoff']), pd.Timestamp(c['decision_asof'])
    if pd.to_datetime(panel.date).max() > cutoff:
        raise ValueError('Cette fonction refuse les observations postérieures à la borne publique.')
    expected_asof = cutoff + pd.offsets.MonthEnd(c['publication_lag_months'])
    if expected_asof > asof:
        raise ValueError('Indice non disponible avec le délai de publication conventionnel.')
    table = features(panel, c['horizon_months'])
    available = table.target_end + pd.offsets.MonthEnd(c['publication_lag_months']) <= asof
    train = table.loc[(table.target_end <= cutoff) & available].dropna(subset=FEATURES + ['target_pp'])
    current = table.loc[table.date.eq(cutoff)].dropna(subset=FEATURES).copy()
    if len(current) != panel.region_id.nunique():
        raise ValueError('Entrées incomplètes pour une zone à la date de décision.')
    current['predicted_return_pp'] = fit_predict(train, current, model_name, c['horizon_months'])
    return current[['region_id', 'region', 'date', 'zhvi', 'predicted_return_pp']].reset_index(drop=True)
