"""Contrôles de données autorisées, sans téléchargeur ni données de révélation."""
import pandas as pd

def validate_panel(panel):
    """Un mois par zone, sans trou ni prix absent, nul ou infini."""
    import numpy as np
    needed = {'region_id', 'region', 'date', 'zhvi'}
    if not needed.issubset(panel):
        raise ValueError('Colonnes de panneau manquantes.')
    p = panel.copy()
    p['date'] = pd.to_datetime(p['date'])
    if p.empty or p.duplicated(['region_id', 'date']).any():
        raise ValueError('Panneau vide ou dates dupliquées.')
    if not np.isfinite(p.zhvi).all() or (p.zhvi <= 0).any():
        raise ValueError('Indices manquants, non finis ou non positifs.')
    for _, group in p.groupby('region_id'):
        dates = pd.DatetimeIndex(group.date.sort_values())
        if not dates.equals(pd.date_range(dates.min(), dates.max(), freq='ME')):
            raise ValueError('Trou mensuel dans une série.')
    return p.sort_values(['region_id', 'date']).reset_index(drop=True)

