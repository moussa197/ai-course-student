"""Contrat de stratégie sans donnée future ; gel et empreinte remis à l'enseignant."""
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
from .config import load_config
from .modeling import MODELS

def validate_economics(economics):
    required = set(load_config()['economics'])
    if set(economics) != required:
        raise ValueError('Paramètres économiques incomplets ou inconnus.')
    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x) for x in economics.values()):
        raise ValueError('Paramètres économiques non numériques ou non finis.')
    if economics['budget_usd'] <= 0 or not 0 < economics['max_zone_fraction'] <= 1:
        raise ValueError('Budget/plafond invalide.')
    if not 0 <= economics['min_cash_fraction'] <= 1:
        raise ValueError('Réserve invalide.')
    for key in ['buy_cost_rate', 'sell_cost_rate', 'annual_holding_rate', 'cash_annual_rate', 'stress_extra_cost_rate']:
        if not 0 <= economics[key] <= 1:
            raise ValueError(f'Taux hors bornes : {key}')
    if not -1 < economics['stress_exit_shock'] <= 0 or economics['safety_margin_pp'] < 0:
        raise ValueError('Stress/marge de sécurité invalide.')
    return economics

def select_allocations(predictions, economics, horizon=6, top_n=5):
    """Allocation égale aux zones dont le gain prévu couvre coûts ET marge de sécurité.

    La marge est un filtre décisionnel, pas une dépense comptable.
    Le plafond porte sur le capital d'achat et la réserve inclut les frais d'entrée.
    """
    e = validate_economics(economics)
    if not isinstance(top_n, int) or isinstance(top_n, bool) or top_n < 0:
        raise ValueError('top_n entier positif ou nul requis.')
    if predictions.region_id.duplicated().any() or not np.isfinite(predictions.predicted_return_pp).all():
        raise ValueError('Prévisions dupliquées ou non finies.')
    rate = predictions.predicted_return_pp / 100
    net = (1 + rate) * (1 - e['sell_cost_rate']) - 1 - e['buy_cost_rate'] - e['annual_holding_rate'] * horizon / 12
    order = predictions.assign(expected_net_pp=100 * net)
    order = order.loc[order.expected_net_pp > e['safety_margin_pp']].sort_values(
        ['expected_net_pp', 'region_id'], ascending=[False, True]).head(top_n)
    if order.empty:
        return []
    available = e['budget_usd'] * (1 - e['min_cash_fraction'])
    each = min(e['budget_usd'] * e['max_zone_fraction'], available / ((1 + e['buy_cost_rate']) * len(order)))
    return [{'region_id': int(row.region_id), 'capital_usd': round(each, 2)} for row in order.itertuples()]

def canonical_bytes(record):
    """JSON canonique pour empreinte SHA256 et contrôle des fichiers remis."""
    return json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def export_strategy(team, model_name, allocations, economics, public_path, output_dir='submissions', config=None):
    """Crée un fichier immuable par convention ; ne prouve pas l'antériorité à lui seul.

    L'enseignant collecte et horodate les empreintes avant révélation.
    """
    c = config or load_config()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', team) or model_name not in MODELS:
        raise ValueError('Nom équipe ASCII simple et modèle autorisé requis.')
    validate_economics(economics)
    record = {'schema_version': 1, 'team': team, 'model': model_name,
              'origin': c['public_cutoff'], 'decision_asof': c['decision_asof'],
              'horizon_months': c['horizon_months'], 'economics': economics,
              'public_sha256': hashlib.sha256(Path(public_path).read_bytes()).hexdigest(),
              'allocations': allocations}
    validate_record(record, set(pd.read_csv(public_path).region_id.unique()), c)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f'{team}.json'
    with path.open('xb') as stream:
        stream.write(canonical_bytes(record))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, digest

def validate_record(record, region_ids, config=None):
    """Refuse NaN, surallocation, identifiants inconnus et paramètres temporels modifiés."""
    c = config or load_config()
    expected = {'schema_version','team','model','origin','decision_asof','horizon_months','economics','public_sha256','allocations'}
    if set(record) != expected or record['schema_version'] != 1 or record['model'] not in MODELS:
        raise ValueError('Schéma de stratégie invalide.')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', record['team']):
        raise ValueError('Équipe invalide.')
    for key, value in [('origin', c['public_cutoff']), ('decision_asof', c['decision_asof']), ('horizon_months', c['horizon_months'])]:
        if record[key] != value:
            raise ValueError(f'Paramètre de séance modifié : {key}')
    if not re.fullmatch(r'[0-9a-f]{64}', record['public_sha256']):
        raise ValueError('Empreinte publique invalide.')
    e = validate_economics(record['economics'])
    if not isinstance(record['allocations'], list):
        raise ValueError('Liste des positions attendue.')
    seen, total = set(), 0.
    for item in record['allocations']:
        if set(item) != {'region_id', 'capital_usd'}:
            raise ValueError('Colonnes de position invalides.')
        rid, value = item['region_id'], item['capital_usd']
        if type(rid) is not int or rid not in region_ids or rid in seen:
            raise ValueError('Zone inconnue ou dupliquée.')
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or value <= 0:
            raise ValueError('Capital non positif ou non fini.')
        if value > e['budget_usd'] * e['max_zone_fraction'] + .01:
            raise ValueError('Concentration excessive.')
        seen.add(rid)
        total += value
    if total * (1 + e['buy_cost_rate']) > e['budget_usd'] * (1 - e['min_cash_fraction']) + .02:
        raise ValueError('Budget ou réserve dépassé.')
    return record
