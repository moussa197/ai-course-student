"""Simulation notionnelle indicielle, distincte du P&L réel Zillow Offers."""
import numpy as np
import pandas as pd
from .decisions import validate_economics

def simulate(allocations, returns, economics, horizon=6, exit_shock=0., extra_cost_rate=0.):
    """Budget inclut achat et frais d'entrée. Frais de vente sur valeur de sortie.

    P&L = C*((1+r)*(1+choc)*(1-frais_vente)-1-frais_achat-portage-coût_sup).
    Marge de sécurité : filtre d'allocation seulement, aucune double comptabilisation.
    """
    e = validate_economics(economics)
    if not isinstance(horizon, int) or horizon < 1 or not -1 < exit_shock <= 0 or not 0 <= extra_cost_rate <= 1:
        raise ValueError('Horizon ou choc invalide.')
    if not {'region_id', 'actual_return_pp'}.issubset(returns) or returns.region_id.duplicated().any():
        raise ValueError('Réalisations invalides.')
    if not np.isfinite(returns.actual_return_pp).all() or (returns.actual_return_pp <= -100).any():
        raise ValueError('Rendements réalisés non finis ou impossibles.')
    positions = pd.DataFrame(allocations, columns=['region_id', 'capital_usd'])
    if positions.region_id.duplicated().any() or not np.isfinite(positions.capital_usd.to_numpy(dtype=float)).all():
        raise ValueError('Positions invalides.')
    if (positions.capital_usd <= 0).any() or (positions.capital_usd > e['budget_usd'] * e['max_zone_fraction'] + .01).any():
        raise ValueError('Capital/concentration invalide.')
    invested = float(positions.capital_usd.sum())
    cash = e['budget_usd'] - invested * (1 + e['buy_cost_rate'])
    if cash < e['budget_usd'] * e['min_cash_fraction'] - .02:
        raise ValueError('Budget ou réserve dépassé.')
    joined = positions.merge(returns, on='region_id', how='left', validate='one_to_one')
    if joined.actual_return_pp.isna().any():
        raise ValueError('Réalisation absente pour une zone investie.')
    net = (1 + joined.actual_return_pp / 100) * (1 + exit_shock) * (1 - e['sell_cost_rate']) - 1 - e['buy_cost_rate'] - e['annual_holding_rate'] * horizon / 12 - extra_cost_rate
    joined['profit_usd'] = joined.capital_usd * net
    joined['exposure_fraction'] = joined.capital_usd / e['budget_usd']
    cash_profit = cash * e['cash_annual_rate'] * horizon / 12
    profit = float(joined.profit_usd.sum() + cash_profit)
    result = {'capital_engaged_usd': invested, 'entry_cost_usd': invested * e['buy_cost_rate'],
              'cash_usd': cash, 'cash_profit_usd': cash_profit, 'profit_usd': profit,
              'return_on_budget_pct': 100 * profit / e['budget_usd'],
              'return_on_engaged_pct': (100 * joined.profit_usd.sum() / invested) if invested else None,
              'losses_usd': max(0., float(-joined.loc[joined.profit_usd < 0, 'profit_usd'].sum())),
              'max_zone_fraction': float(joined.exposure_fraction.max()) if len(joined) else 0.,
              'number_zones': len(joined), 'final_wealth_usd': e['budget_usd'] + profit}
    return result, joined
