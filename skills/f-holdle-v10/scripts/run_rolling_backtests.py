#!/usr/bin/env python3
"""Run audited HOLDLE v10 rolling-window backtests on the locked top-strategy union."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(os.environ.get('HOLDLE_ROOT', Path.home() / 'code/holdle')).expanduser()
TRAIN = ROOT / '04_训练记录'
DEV = TRAIN / 'v10_search'
FULL = TRAIN / 'v10_2020_2026_full_rank'
LATEST = TRAIN / 'v10_composite_champion_2022_to_latest_rerun'
DEFAULT_PROJECT = TRAIN / 'v10_top_union_rolling_2010_2026'

PRICE_OLD = DEV / 'data/raw/v10_prices_2006_2019.parquet'
PRICE_NEW = FULL / 'data/raw/v10_prices_2006_20260818.parquet'
PRICE_SUPPLEMENT = LATEST / 'data/raw/latest_price_supplement.parquet'
SIGNALS_OLD = DEV / 'data/derived/v10_entry_window_signals_2010_2019.parquet'
SIGNALS_NEW = FULL / 'data/derived/v10_entry_window_signals_2020_2026.parquet'
MEMBERSHIP_OLD = DEV / 'data/derived/v10_selection_membership_2010_2019.parquet'
MEMBERSHIP_NEW = FULL / 'data/derived/v10_selection_membership_2019_2026.parquet'
COMPOSITE_RANK = FULL / 'results/top_rankings/top100_composite.csv'
NET_VALUE_RANK = FULL / 'results/top_rankings/top100_net_value.csv'
SELECTION_CONFIGS = FULL / 'candidates/selection_configs.jsonl'
ENTRY_CONFIGS = FULL / 'candidates/entry_configs.jsonl'
PORTFOLIO_CONFIGS = FULL / 'candidates/portfolio_configs.jsonl'

START = pd.Timestamp('2010-01-01')
HORIZONS = (3, 5, 6, 7)
INITIAL_CAPITAL = 100_000.0
POSITION_SIZE = 10_000.0
CHAMPION_SELECTION = 'sel-1ec754339a53a397'
CHAMPION_ENTRY = 'ent-6fa74d3c9181a9b9'
CHAMPION_SOURCE_PORTFOLIO = 'port-ed1797c5a175944a'
CHAMPION_FULL_PORTFOLIO = 'port-5b717f19eed2a045'

sys.path.insert(0, str(TRAIN / 'v10_search'))
sys.path.insert(0, str(TRAIN))
sys.path.insert(0, str(FULL))
CODEX_HOME = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')).expanduser()
sys.path.insert(0, str(CODEX_HOME / 'skills/f-holdle/scripts'))

import build_entry_signal_cache as entry_core  # noqa: E402
import run_event_grid as event_core  # noqa: E402
import run_holdle_v10_portfolio_search as portfolio_core  # noqa: E402
from unified_backtest_v2 import resample_weekly  # noqa: E402

_core_spec = importlib.util.spec_from_file_location(
    'v10_latest_core', TRAIN / 'v10_top10_2022_to_latest_rerun/run_top10_rerun.py'
)
latest_core = importlib.util.module_from_spec(_core_spec)
sys.modules[_core_spec.name] = latest_core
_core_spec.loader.exec_module(latest_core)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    os.replace(temporary, path)


def atomic_text(path: Path, payload: str) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(payload, encoding='utf-8')
    os.replace(temporary, path)


def atomic_parquet(path: Path, frame: pd.DataFrame) -> None:
    temporary = path.with_suffix('.parquet.tmp')
    frame.to_parquet(temporary, index=False, compression='zstd')
    os.replace(temporary, path)


def scalar(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def load_strategy_union() -> tuple[pd.DataFrame, pd.DataFrame, dict, dict, dict]:
    composite = pd.read_csv(COMPOSITE_RANK).head(50).copy()
    net_value = pd.read_csv(NET_VALUE_RANK).head(20).copy()
    composite['composite_rank'] = np.arange(1, 51)
    net_value['net_value_rank'] = np.arange(1, 21)
    keys = ['selection_config_id', 'entry_config_id', 'portfolio_config_id']
    source_rows: dict[tuple, dict] = {}
    for label, frame in [('composite_top50', composite), ('net_value_top20', net_value)]:
        for row in frame.itertuples(index=False):
            key = tuple(getattr(row, column) for column in keys)
            record = source_rows.setdefault(key, {
                **dict(zip(keys, key)), 'in_composite_top50': False, 'in_net_value_top20': False,
                'composite_rank': np.nan, 'net_value_rank': np.nan,
                'source_max_positions': int(row.max_positions),
                'source_max_sw1_positions': int(row.max_sw1_positions),
                'source_max_sw3_positions': int(row.max_sw3_positions),
            })
            record[f'in_{label}'] = True
            record['composite_rank' if label == 'composite_top50' else 'net_value_rank'] = int(
                getattr(row, 'composite_rank' if label == 'composite_top50' else 'net_value_rank')
            )
    source = pd.DataFrame(source_rows.values())
    if len(source) != 67 or source.duplicated(keys).any():
        raise AssertionError(f'expected 67 unique source triples, got {len(source)}')

    selection = pd.read_json(SELECTION_CONFIGS, lines=True).set_index('selection_config_id').to_dict('index')
    entry = pd.read_json(ENTRY_CONFIGS, lines=True).set_index('entry_config_id').to_dict('index')
    portfolios_frame = pd.read_json(PORTFOLIO_CONFIGS, lines=True)
    portfolio = portfolios_frame.set_index('portfolio_config_id').to_dict('index')
    target_lookup = portfolios_frame[portfolios_frame['max_positions'] == 10].set_index(
        ['max_sw1_positions', 'max_sw3_positions']
    )['portfolio_config_id'].to_dict()

    effective_rows: dict[tuple, dict] = {}
    for row in source.itertuples(index=False):
        source_portfolio = portfolio[row.portfolio_config_id]
        cap_key = (int(source_portfolio['max_sw1_positions']), int(source_portfolio['max_sw3_positions']))
        if cap_key not in target_lookup:
            raise AssertionError(f'no max-10 portfolio for concentration caps {cap_key}')
        target_portfolio_id = target_lookup[cap_key]
        effective_key = (row.selection_config_id, row.entry_config_id, target_portfolio_id)
        record = effective_rows.setdefault(effective_key, {
            'selection_config_id': row.selection_config_id,
            'entry_config_id': row.entry_config_id,
            'effective_portfolio_config_id': target_portfolio_id,
            'max_positions': 10,
            'max_sw1_positions': cap_key[0],
            'max_sw3_positions': cap_key[1],
            'source_strategy_count': 0,
            'in_composite_top50': False,
            'in_net_value_top20': False,
            'best_composite_rank': np.nan,
            'best_net_value_rank': np.nan,
            'source_portfolio_config_ids': [],
        })
        record['source_strategy_count'] += 1
        record['in_composite_top50'] |= bool(row.in_composite_top50)
        record['in_net_value_top20'] |= bool(row.in_net_value_top20)
        if pd.notna(row.composite_rank):
            current = record['best_composite_rank']
            record['best_composite_rank'] = int(row.composite_rank) if pd.isna(current) else min(int(current), int(row.composite_rank))
        if pd.notna(row.net_value_rank):
            current = record['best_net_value_rank']
            record['best_net_value_rank'] = int(row.net_value_rank) if pd.isna(current) else min(int(current), int(row.net_value_rank))
        record['source_portfolio_config_ids'].append(row.portfolio_config_id)
    effective = pd.DataFrame(effective_rows.values())
    if len(effective) != 66:
        raise AssertionError(f'expected 66 effective configurations after capacity override, got {len(effective)}')
    effective['effective_strategy_id'] = effective.apply(
        lambda row: 'v10f-' + hashlib.sha256(
            f"{row.selection_config_id}|{row.entry_config_id}|{row.effective_portfolio_config_id}".encode()
        ).hexdigest()[:16], axis=1,
    )
    if not (
        (effective['selection_config_id'] == CHAMPION_SELECTION)
        & (effective['entry_config_id'] == CHAMPION_ENTRY)
        & (effective['effective_portfolio_config_id'] == CHAMPION_FULL_PORTFOLIO)
    ).any():
        raise AssertionError('capacity-overridden composite champion is missing')
    return source, effective, selection, entry, portfolio


def load_prices() -> tuple[pd.DataFrame, pd.Timestamp, dict]:
    old = pd.read_parquet(PRICE_OLD)
    new = pd.read_parquet(PRICE_NEW)
    supplement = pd.read_parquet(PRICE_SUPPLEMENT)
    for frame in [old, new, supplement]:
        frame['date'] = pd.to_datetime(frame['date'], errors='raise')
    overlap = old.merge(new, on=['code', 'date'], suffixes=('_old', '_new'))
    errors = {
        column: float((overlap[f'{column}_old'] - overlap[f'{column}_new']).abs().max())
        for column in ['open', 'high', 'low', 'close']
    }
    if any(value > 1e-6 for value in errors.values()):
        raise AssertionError(f'old/new adjusted-price overlap mismatch: {errors}')
    prices = pd.concat([old, new, supplement], ignore_index=True)
    prices = prices.sort_values(['code', 'date']).drop_duplicates(['code', 'date'], keep='last')
    cutoff = pd.Timestamp(prices['date'].max()).normalize()
    if cutoff < pd.Timestamp('2026-08-20'):
        raise AssertionError(f'local price cutoff unexpectedly old: {cutoff.date()}')
    audit = {
        'old_price_period': [str(old['date'].min().date()), str(old['date'].max().date())],
        'new_price_period': [str(new['date'].min().date()), str(new['date'].max().date())],
        'supplement_period': [str(supplement['date'].min().date()), str(supplement['date'].max().date())],
        'combined_period': [str(prices['date'].min().date()), str(cutoff.date())],
        'combined_rows': len(prices), 'combined_codes': int(prices['code'].nunique()),
        'duplicate_code_date_rows': int(prices.duplicated(['code', 'date']).sum()),
        'old_new_overlap_rows': len(overlap),
        'old_new_adjusted_ohlc_max_abs_error': errors,
        'input_sha256': {str(path): sha256_file(path) for path in [PRICE_OLD, PRICE_NEW, PRICE_SUPPLEMENT]},
    }
    return prices, cutoff, audit


def load_membership(selected_ids: set[str]) -> tuple[pd.DataFrame, dict]:
    old = pd.read_parquet(MEMBERSHIP_OLD)
    new = pd.read_parquet(MEMBERSHIP_NEW)
    old = old[old['selection_config_id'].isin(selected_ids)].copy()
    new = new[new['selection_config_id'].isin(selected_ids)].copy()
    keys = ['selection_config_id', 'selection_year', 'code']
    overlap = old.merge(new, on=keys, suffixes=('_old', '_new'))
    if len(overlap):
        score_error = float((overlap['selection_score_v10_old'] - overlap['selection_score_v10_new']).abs().max())
        industry_match = bool((overlap['industry_old'].astype(str) == overlap['industry_new'].astype(str)).all())
        if score_error > 1e-8 or not industry_match:
            raise AssertionError('2019 membership overlap is inconsistent')
    else:
        score_error, industry_match = None, True
    membership = pd.concat([old, new], ignore_index=True)
    membership = membership.sort_values(keys).drop_duplicates(keys, keep='last')
    missing = selected_ids - set(membership['selection_config_id'])
    if missing:
        raise AssertionError(f'membership misses selected configurations: {sorted(missing)}')
    return membership, {
        'period': [int(membership['selection_year'].min()), int(membership['selection_year'].max())],
        'rows': len(membership), 'codes': int(membership['code'].nunique()),
        'selection_configs': int(membership['selection_config_id'].nunique()),
        'duplicate_keys': int(membership.duplicated(keys).sum()),
        'overlap_rows': len(overlap), 'overlap_score_max_abs_error': score_error,
        'overlap_industry_all_equal': industry_match,
        'input_sha256': {str(path): sha256_file(path) for path in [MEMBERSHIP_OLD, MEMBERSHIP_NEW]},
    }


def regenerate_signals(selected_entry_ids: set[str], membership: pd.DataFrame, prices: pd.DataFrame,
                       cutoff: pd.Timestamp, checkpoint: Path) -> tuple[pd.DataFrame, dict]:
    """Regenerate one continuous 2010-latest signal path, avoiding legacy split-boundary loss."""
    entry_core.SEGMENTS = {'rolling_full_timeline': (START, cutoff)}
    entry_core.simulate_exit = latest_core.simulate_exit_asof
    all_configs = entry_core.entry_configs()
    required_codes = sorted(membership['code'].unique())
    names = membership.sort_values(['selection_year', 'code']).drop_duplicates('code', keep='last').set_index('code')['name'].to_dict()
    price_groups = {code: group.sort_values('date').copy() for code, group in prices.groupby('code', sort=False)}
    missing = sorted(set(required_codes) - set(price_groups))
    if missing:
        raise AssertionError(f'price panel misses {len(missing)} selected-universe codes')
    records = []
    for index, code in enumerate(required_codes, start=1):
        code_records = entry_core.process_code(code, names.get(code, code), price_groups[code], all_configs)
        records.extend(row for row in code_records if row['entry_config_id'] in selected_entry_ids)
        if index % 100 == 0 or index == len(required_codes):
            atomic_json(checkpoint, {
                'state': 'regenerating_continuous_signals', 'completed_codes': index,
                'total_codes': len(required_codes), 'updated_at_epoch': time.time(),
            })
            print(f'continuous signal regeneration: {index}/{len(required_codes)}', flush=True)
    signals = pd.DataFrame(records)
    date_columns = [
        'window_start', 'window_end', 'window_blocked_until', 'entry_date', 'green_bar_date',
        'exit_date', 'last_date', 'single_stock_block_until',
    ]
    for column in date_columns:
        signals[column] = pd.to_datetime(signals[column], errors='coerce')
    # Monthly signals require a completed month; the current August 2026 bar is incomplete.
    if cutoff < cutoff.to_period('M').end_time.normalize():
        signals = signals[signals['window_start'].dt.to_period('M') < cutoff.to_period('M')].copy()
    duplicate_keys = ['entry_config_id', 'code', 'window_start']
    if signals.duplicated(duplicate_keys).any():
        raise AssertionError(f'regenerated signals contain {int(signals.duplicated(duplicate_keys).sum())} duplicate keys')
    mask = signals['entry_status'] == 'entered'
    if signals.loc[mask, 'return_pct'].isna().any():
        raise AssertionError('one or more regenerated entered signals lack latest valuation')
    boundary_entries = signals[
        mask & signals['window_start'].dt.month.eq(12) & signals['entry_date'].dt.year.gt(signals['window_start'].dt.year)
    ]
    return signals, {
        'method': 'continuous_regeneration_2010_to_latest',
        'legacy_split_files_used_as_signals': False,
        'rows': len(signals), 'codes': int(signals['code'].nunique()),
        'entry_configs': int(signals['entry_config_id'].nunique()),
        'window_period': [str(signals['window_start'].min().date()), str(signals['window_start'].max().date())],
        'entered_rows': int(mask.sum()),
        'cross_year_december_window_entries_preserved': len(boundary_entries),
        'engine_sha256': sha256_file(Path(entry_core.__file__)),
        'exit_engine_sha256': sha256_file(Path(latest_core.__file__)),
    }


def generate_windows(cutoff: pd.Timestamp) -> pd.DataFrame:
    rows = []
    for years in HORIZONS:
        for start_year in range(START.year, cutoff.year + 1):
            start = pd.Timestamp(start_year, 1, 1)
            end = pd.Timestamp(start_year + years - 1, 12, 31)
            if end <= cutoff:
                rows.append({
                    'window_id': f'cal_{years}y_{start_year}_{start_year + years - 1}',
                    'horizon_years': years, 'window_type': 'full_calendar',
                    'window_start': start, 'window_end': end,
                })
        trailing_start = (cutoff - pd.DateOffset(years=years) + pd.Timedelta(days=1)).normalize()
        rows.append({
            'window_id': f'trail_{years}y_to_{cutoff.strftime("%Y%m%d")}',
            'horizon_years': years, 'window_type': 'trailing_to_latest',
            'window_start': trailing_start, 'window_end': cutoff,
        })
    windows = pd.DataFrame(rows).drop_duplicates(['window_start', 'window_end', 'horizon_years'])
    if set(windows['horizon_years']) != set(HORIZONS) or len(windows) != 51:
        raise AssertionError(f'expected 51 rolling windows, got {len(windows)}')
    return windows.sort_values(['horizon_years', 'window_start', 'window_type']).reset_index(drop=True)


def signals_asof(signals: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp,
                  close: pd.DataFrame) -> pd.DataFrame:
    frame = signals[signals['window_start'].between(start, end)].copy()
    entry_mask = frame['entry_status'] == 'entered'
    outside = entry_mask & (frame['entry_date'] > end)
    frame.loc[outside, 'entry_status'] = 'entry_outside_segment'
    frame.loc[outside, 'window_blocked_until'] = end
    active = frame['entry_status'] == 'entered'
    beyond = active & (frame['exit_date'].isna() | (frame['exit_date'] > end))
    if beyond.any():
        available = close.loc[close.index <= end]
        if available.empty:
            raise AssertionError(f'no close prices at window end {end.date()}')
        last_date = available.index[-1]
        last_marks = available.iloc[-1]
        marks = frame.loc[beyond, 'code'].map(last_marks)
        if marks.isna().any():
            raise AssertionError('missing end mark for one or more holding signals')
        frame.loc[beyond, 'exit_status'] = 'holding'
        frame.loc[beyond, 'exit_date'] = pd.NaT
        frame.loc[beyond, 'exit_price'] = np.nan
        frame.loc[beyond, 'last_date'] = last_date
        frame.loc[beyond, 'last_price'] = marks.to_numpy()
        frame.loc[beyond, 'safety_line'] = np.nan
        frame.loc[beyond, 'exit_reason'] = ''
        frame.loc[beyond, 'return_pct'] = (
            marks.to_numpy() / frame.loc[beyond, 'entry_price'].astype(float).to_numpy() - 1
        ) * 100
        frame.loc[beyond, 'single_stock_block_until'] = last_date
    return frame


def enrich_trades(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return trades
    frame = trades.copy()
    for column in ['entry_date', 'exit_date', 'last_date']:
        frame[column] = pd.to_datetime(frame[column], errors='coerce')
    frame['position_notional_cny'] = POSITION_SIZE
    frame['gross_pnl_cny'] = frame['return_pct'].astype(float) * POSITION_SIZE / 100
    frame['buy_cost_cny'] = frame['position_notional_cny'].map(lambda value: event_core.side_cost(value, 'buy'))
    frame['sell_cost_cny'] = frame.apply(
        lambda row: event_core.side_cost(POSITION_SIZE * (1 + float(row.return_pct) / 100), 'sell')
        if pd.notna(row.exit_date) else 0.0, axis=1,
    )
    frame['net_pnl_cny'] = frame['gross_pnl_cny'] - frame['buy_cost_cny'] - frame['sell_cost_cny']
    return frame


def active_cap_maxima(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {'positions': 0, 'sw1': 0, 'sw3': 0}
    events = sorted(set(pd.to_datetime(trades['entry_date'])) | set(pd.to_datetime(trades['exit_date']).dropna()))
    maxima = {'positions': 0, 'sw1': 0, 'sw3': 0}
    for date in events:
        active = trades[
            (trades['entry_date'] <= date)
            & (trades['exit_date'].isna() | (trades['exit_date'] > date))
        ]
        maxima['positions'] = max(maxima['positions'], len(active))
        if len(active):
            maxima['sw1'] = max(maxima['sw1'], int(active.groupby('sw1').size().max()))
            maxima['sw3'] = max(maxima['sw3'], int(active.groupby('industry').size().max()))
    return maxima


def run_windows(windows: pd.DataFrame, effective: pd.DataFrame, membership: pd.DataFrame,
                signals: pd.DataFrame, prices: pd.DataFrame, project: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    checkpoint = project / 'checkpoints/state.json'
    close = prices.pivot(index='date', columns='code', values='close').sort_index().ffill()
    metrics_rows, trade_frames = [], []
    total = len(windows) * len(effective)
    completed = 0
    for window in windows.itertuples(index=False):
        window_signals = signals_asof(signals, window.window_start, window.window_end, close)
        pair_candidates = {}
        for selection_id, entry_id in effective[['selection_config_id', 'entry_config_id']].drop_duplicates().itertuples(index=False):
            member = membership[membership['selection_config_id'] == selection_id]
            selected_signals = window_signals[window_signals['entry_config_id'] == entry_id]
            candidates = entry_core.assemble_candidates(selected_signals, member)
            if len(candidates):
                candidates = candidates[pd.to_datetime(candidates['entry_date']).between(window.window_start, window.window_end)].copy()
                candidates['selection_score'] = pd.to_numeric(candidates['selection_score_v10'], errors='raise')
                candidates['segment'] = window.window_id
            pair_candidates[(selection_id, entry_id)] = candidates

        event_core.SEGMENT_ENDS[window.window_id] = window.window_end
        portfolio_core.SEGMENTS[window.window_id] = (window.window_start, window.window_end)
        for strategy in effective.itertuples(index=False):
            candidates = pair_candidates[(strategy.selection_config_id, strategy.entry_config_id)]
            config = {
                'portfolio_config_id': strategy.effective_portfolio_config_id,
                'max_positions': int(strategy.max_positions),
                'max_sw1_positions': int(strategy.max_sw1_positions),
                'max_sw3_positions': int(strategy.max_sw3_positions),
            }
            prepared = event_core.prepare_segment(candidates, window.window_id)
            event_metrics, rows = event_core.simulate_prepared(prepared, config, window.window_id)
            trades = enrich_trades(pd.DataFrame(rows))
            variant = portfolio_core.PortfolioVariant(
                config['max_positions'], config['max_sw1_positions'], config['max_sw3_positions']
            )
            nav = portfolio_core.build_nav(trades, close, window.window_id)
            rejected = {
                key: int(event_metrics[f'rejected_{key}'])
                for key in ['position_cap', 'sw1_cap', 'sw3_cap', 'cash']
            }
            daily_metrics = portfolio_core.compute_metrics(window.window_id, variant, nav, trades, rejected)
            nav_error = abs(float(nav.iloc[-1]['net_nav']) - float(event_metrics['final_net_value']))
            if nav_error > 0.05:
                raise AssertionError(f'NAV mismatch {window.window_id}/{strategy.effective_strategy_id}: {nav_error}')
            caps = active_cap_maxima(trades)
            if caps['positions'] > config['max_positions'] or caps['sw1'] > config['max_sw1_positions'] or caps['sw3'] > config['max_sw3_positions']:
                raise AssertionError(f'capacity violation {window.window_id}/{strategy.effective_strategy_id}: {caps}')
            last_trading = pd.Timestamp(nav.iloc[-1]['date'])
            metrics_rows.append({
                'window_id': window.window_id, 'horizon_years': int(window.horizon_years),
                'window_type': window.window_type, 'window_start': window.window_start,
                'window_end': window.window_end, 'last_trading_date': last_trading,
                'effective_strategy_id': strategy.effective_strategy_id,
                'selection_config_id': strategy.selection_config_id,
                'entry_config_id': strategy.entry_config_id,
                'effective_portfolio_config_id': strategy.effective_portfolio_config_id,
                'source_strategy_count': int(strategy.source_strategy_count),
                'in_composite_top50': bool(strategy.in_composite_top50),
                'in_net_value_top20': bool(strategy.in_net_value_top20),
                'best_composite_rank': scalar(strategy.best_composite_rank),
                'best_net_value_rank': scalar(strategy.best_net_value_rank),
                **{key: scalar(value) for key, value in daily_metrics.items()},
                'event_vs_daily_final_nav_abs_error_cny': nav_error,
                'audited_max_concurrent_positions': caps['positions'],
                'audited_max_concurrent_sw1': caps['sw1'],
                'audited_max_concurrent_sw3': caps['sw3'],
            })
            if len(trades):
                trades.insert(0, 'effective_strategy_id', strategy.effective_strategy_id)
                trades.insert(0, 'window_id', window.window_id)
                trades['horizon_years'] = int(window.horizon_years)
                trades['window_type'] = window.window_type
                trade_frames.append(trades)
            completed += 1
        atomic_json(checkpoint, {
            'state': 'running_windows', 'completed_strategy_windows': completed,
            'total_strategy_windows': total, 'last_window': window.window_id,
            'updated_at_epoch': time.time(),
        })
        print(f'window complete: {window.window_id} ({completed}/{total})', flush=True)
    metrics = pd.DataFrame(metrics_rows)
    trades = pd.concat(trade_frames, ignore_index=True) if trade_frames else pd.DataFrame()
    return metrics, trades


def build_summaries(metrics: pd.DataFrame, effective: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    full = metrics[metrics['window_type'] == 'full_calendar'].copy()
    grouped = full.groupby([
        'effective_strategy_id', 'selection_config_id', 'entry_config_id',
        'effective_portfolio_config_id', 'horizon_years',
    ], as_index=False).agg(
        windows=('window_id', 'nunique'),
        median_annual_return_pct=('annual_return_pct', 'median'),
        minimum_annual_return_pct=('annual_return_pct', 'min'),
        median_total_return_pct=('total_return_pct', 'median'),
        positive_window_rate_pct=('total_return_pct', lambda values: float((values > 0).mean() * 100)),
        worst_max_drawdown_pct=('max_drawdown_pct', 'min'),
        median_profit_factor=('profit_factor', 'median'),
        median_without_top3_net_pnl_cny=('without_top3_net_pnl_cny', 'median'),
        median_capital_utilization_pct=('average_capital_utilization_pct', 'median'),
    )
    grouped['horizon_rank_by_median_annual'] = grouped.groupby('horizon_years')['median_annual_return_pct'].rank(
        method='min', ascending=False
    ).astype(int)
    champions = grouped.sort_values(
        ['horizon_years', 'median_annual_return_pct', 'positive_window_rate_pct', 'minimum_annual_return_pct'],
        ascending=[True, False, False, False],
    ).groupby('horizon_years', as_index=False).head(1)
    return grouped.sort_values(['horizon_years', 'horizon_rank_by_median_annual']), champions


def completion_audit(source: pd.DataFrame, effective: pd.DataFrame, windows: pd.DataFrame,
                     metrics: pd.DataFrame, trades: pd.DataFrame, cutoff: pd.Timestamp,
                     data_audit: dict) -> dict:
    expected_rows = len(windows) * len(effective)
    if len(metrics) != expected_rows or metrics.duplicated(['window_id', 'effective_strategy_id']).any():
        raise AssertionError('strategy-window result coverage is incomplete or duplicated')
    fixed = trades[trades['exit_reason'] == 'fixed_cost_stop'] if len(trades) else trades
    weekly = trades[trades['exit_reason'] == 'weekly_low_close_confirmed'] if len(trades) else trades
    fixed_error = float((fixed['exit_price'] - fixed['entry_price'] * 0.60).abs().max()) if len(fixed) else 0.0
    if fixed_error > 1e-8:
        raise AssertionError(f'fixed stop invariant failed: {fixed_error}')
    if len(weekly) and not (weekly['exit_price'] < weekly['safety_line']).all():
        raise AssertionError('weekly confirmed exits are not below the safety line')
    if float(metrics['event_vs_daily_final_nav_abs_error_cny'].max()) > 0.05:
        raise AssertionError('event/daily NAV reconciliation failed')
    if (metrics['audited_max_concurrent_positions'] > metrics['max_positions']).any():
        raise AssertionError('total position cap failed')
    if (metrics['audited_max_concurrent_sw1'] > metrics['max_sw1_positions']).any():
        raise AssertionError('SW1 concentration cap failed')
    if (metrics['audited_max_concurrent_sw3'] > metrics['max_sw3_positions']).any():
        raise AssertionError('SW3 concentration cap failed')
    return {
        'status': 'complete', 'local_data_cutoff': str(cutoff.date()),
        'research_timeline': [str(START.date()), str(cutoff.date())],
        'source_strategy_triples': len(source), 'effective_strategies_after_capacity_override': len(effective),
        'rolling_windows': len(windows), 'strategy_window_results': len(metrics),
        'expected_strategy_window_results': expected_rows,
        'full_calendar_windows': int((windows['window_type'] == 'full_calendar').sum()),
        'trailing_to_latest_windows': int((windows['window_type'] == 'trailing_to_latest').sum()),
        'fixed_stop_rows': len(fixed), 'fixed_stop_max_price_error': fixed_error,
        'weekly_close_confirmed_rows': len(weekly),
        'weekly_all_exit_closes_below_safety_line': True,
        'max_event_vs_daily_nav_error_cny': float(metrics['event_vs_daily_final_nav_abs_error_cny'].max()),
        'all_total_position_caps_respected': True,
        'all_sw1_caps_respected': True, 'all_sw3_caps_respected': True,
        'all_initial_capital_cny': INITIAL_CAPITAL, 'all_position_notional_cny': POSITION_SIZE,
        'data_audit': data_audit,
    }


def write_report(project: Path, cutoff: pd.Timestamp, source: pd.DataFrame, effective: pd.DataFrame,
                 windows: pd.DataFrame, metrics: pd.DataFrame, stability: pd.DataFrame,
                 champions: pd.DataFrame, trades: pd.DataFrame, audit: dict) -> Path:
    report = TRAIN / 'HOLDLE_v10综合前50并净值前20_3-5-6-7年滚动回测报告.md'
    champion_id = effective[
        (effective['selection_config_id'] == CHAMPION_SELECTION)
        & (effective['entry_config_id'] == CHAMPION_ENTRY)
        & (effective['effective_portfolio_config_id'] == CHAMPION_FULL_PORTFOLIO)
    ].iloc[0]['effective_strategy_id']
    champion_metrics = metrics[metrics['effective_strategy_id'] == champion_id]
    horizon_rows = []
    for years in HORIZONS:
        part = champion_metrics[(champion_metrics['horizon_years'] == years) & (champion_metrics['window_type'] == 'full_calendar')]
        horizon_rows.append(
            f"| {years}年 | {len(part)} | {part['annual_return_pct'].median():.2f}% | "
            f"{part['annual_return_pct'].min():.2f}% | {(part['total_return_pct'] > 0).mean() * 100:.1f}% | "
            f"{part['max_drawdown_pct'].min():.2f}% | {part['without_top3_net_pnl_cny'].median():,.2f} |"
        )
    top_rows = []
    for row in champions.itertuples(index=False):
        top_rows.append(
            f"| {int(row.horizon_years)}年 | `{row.effective_strategy_id}` | `{row.selection_config_id}` | "
            f"`{row.entry_config_id}` | `{row.effective_portfolio_config_id}` | "
            f"{row.median_annual_return_pct:.2f}% | {row.positive_window_rate_pct:.1f}% | "
            f"{row.minimum_annual_return_pct:.2f}% |"
        )
    trailing = champion_metrics[champion_metrics['window_type'] == 'trailing_to_latest'].sort_values('horizon_years')
    trailing_rows = '\n'.join(
        f"| {int(row.horizon_years)}年 | {pd.Timestamp(row.window_start).date()} | {pd.Timestamp(row.window_end).date()} | "
        f"{row.final_net_value:,.2f} | {row.total_return_pct:.2f}% | {row.annual_return_pct:.2f}% | "
        f"{row.max_drawdown_pct:.2f}% | {int(row.trades)} / {int(row.completed_trades)} |"
        for row in trailing.itertuples(index=False)
    )
    text = f"""# HOLDLE v10 综合前50∪净值前20：3/5/6/7年滚动回测

## 口径

- 本地可研究交易时间轴：2010-01-01至{cutoff.date()}；后复权价格预热始于{audit['data_audit']['prices']['combined_period'][0]}。
- 原综合前50与原净值前20共{len(source)}个不重复源策略；将总仓上限统一覆盖为10后，共{len(effective)}个不重复有效配置。只改总仓位，保留每个源组合的申万一级/三级上限。
- 当前 v10 综合冠军拉满版：`{CHAMPION_SELECTION}` / `{CHAMPION_ENTRY}` / `{CHAMPION_FULL_PORTFOLIO}`（10/2/2）。
- 每个窗口独立以100,000元起跑，每仓10,000元；固定成本-40%日内止损，官网周K最低价与完整周收盘双确认止盈。
- 共{len(windows)}个窗口：{int((windows.window_type == 'full_calendar').sum())}个完整日历滚动窗口，另有4个截至最新交易日的等长尾部窗口。窗口每年步进，因此高度重叠，不能当作独立样本。

## 原综合冠军拉满版：完整日历窗口稳定性

| 周期 | 窗口数 | 年化中位数 | 最低年化 | 正收益窗口 | 最差最大回撤 | 剔除头3笔后损益中位数 |
|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(horizon_rows)}

## 原综合冠军拉满版：截至最新交易日

| 周期 | 开始 | 结束 | 期末净值 | 总收益 | 年化 | 最大回撤 | 交易/已结束 |
|---:|---:|---:|---:|---:|---:|---:|---:|
{trailing_rows}

## 每个周期的回看稳定性第一

下表按完整日历窗口的年化收益中位数排序，只是回看描述，不替代已冻结的 v10 综合冠军。

| 周期 | 有效策略 | 选股 | 买入 | 10仓组合 | 年化中位数 | 正收益窗口 | 最低年化 |
|---:|---|---|---|---|---:|---:|---:|
{chr(10).join(top_rows)}

## 风险与审计

- 固定止损价最大误差：{audit['fixed_stop_max_price_error']:.12g}；事件净值与逐日净值最大误差：{audit['max_event_vs_daily_nav_error_cny']:.12g}元。
- 全部总仓、申万一级和申万三级并发约束均通过逐窗口逐策略复核。
- 候选集来自2020–2026排名；2010–2019与2020–2026滚动结果都是事后稳健性检查，不是未触碰盲测。
- 报告使用后复权研究价格，不是可直接照抄的实盘报价；回撤只报告，不参与卖出。

详细结果位于 `{project}`。
"""
    atomic_text(report, text)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, default=DEFAULT_PROJECT)
    args = parser.parse_args()
    project = args.project.resolve()
    config_dir, derived_dir = project / 'config', project / 'data/derived'
    results_dir, reports_dir, checkpoint_dir = project / 'results', project / 'reports', project / 'checkpoints'
    for directory in [config_dir, derived_dir, results_dir, reports_dir, checkpoint_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    started = time.time()
    checkpoint = checkpoint_dir / 'state.json'
    atomic_json(checkpoint, {'state': 'starting', 'updated_at_epoch': started})

    source, effective, selection, entry, portfolios = load_strategy_union()
    prices, cutoff, price_audit = load_prices()
    membership, membership_audit = load_membership(set(effective['selection_config_id']))
    windows = generate_windows(cutoff)
    signals, signal_audit = regenerate_signals(
        set(effective['entry_config_id']), membership, prices, cutoff, checkpoint
    )
    data_audit = {'prices': price_audit, 'membership': membership_audit, 'signals': signal_audit}

    atomic_parquet(derived_dir / 'source_strategy_union.parquet', source)
    source.to_csv(derived_dir / 'source_strategy_union.csv', index=False)
    atomic_parquet(derived_dir / 'effective_strategy_union.parquet', effective)
    effective.to_csv(derived_dir / 'effective_strategy_union.csv', index=False)
    atomic_parquet(derived_dir / 'windows.parquet', windows)
    windows.to_csv(derived_dir / 'windows.csv', index=False)
    atomic_parquet(derived_dir / 'selected_entry_signals_enriched_to_latest.parquet', signals)
    atomic_json(reports_dir / 'data_timeline_audit.json', data_audit)

    lock = {
        'status': 'locked', 'created_at_epoch': time.time(),
        'research_timeline': [str(START.date()), str(cutoff.date())],
        'horizons_years': list(HORIZONS), 'window_generation': 'annual_step_full_calendar_plus_trailing_to_latest',
        'source_strategy_union': {'composite_top': 50, 'net_value_top': 20, 'unique_triples': len(source)},
        'effective_strategies_after_max10_override': len(effective),
        'capacity_override': 'max_positions=10; preserve source max_sw1_positions and max_sw3_positions',
        'champion': {
            'selection_config_id': CHAMPION_SELECTION, 'entry_config_id': CHAMPION_ENTRY,
            'source_portfolio_config_id': CHAMPION_SOURCE_PORTFOLIO,
            'effective_portfolio_config_id': CHAMPION_FULL_PORTFOLIO,
        },
        'fixed_rules': {
            'initial_capital_cny': INITIAL_CAPITAL, 'position_notional_cny': POSITION_SIZE,
            'fixed_stop': 'entry_cost_times_0.60_intraday_low_trigger',
            'take_profit': 'website_weekly_effective_low_week_low_and_completed_week_close_confirmation',
            'commission_rate': event_core.COMMISSION_RATE, 'minimum_commission_cny': event_core.MIN_COMMISSION,
            'one_way_slippage_bps': event_core.SLIPPAGE_BPS, 'sell_stamp_tax_rate': event_core.STAMP_TAX,
        },
        'code_sha256': {
            str(Path(__file__).resolve()): sha256_file(Path(__file__).resolve()),
            str(Path(__file__).resolve().parent.parent / 'SKILL.md'): sha256_file(Path(__file__).resolve().parent.parent / 'SKILL.md'),
            str(Path(__file__).resolve().parent.parent / 'references/champion-contract.md'): sha256_file(
                Path(__file__).resolve().parent.parent / 'references/champion-contract.md'
            ),
            str(Path(event_core.__file__).resolve()): sha256_file(Path(event_core.__file__).resolve()),
            str(Path(portfolio_core.__file__).resolve()): sha256_file(Path(portfolio_core.__file__).resolve()),
        },
        'source_sha256': {str(path): sha256_file(path) for path in [
            COMPOSITE_RANK, NET_VALUE_RANK, SELECTION_CONFIGS, ENTRY_CONFIGS, PORTFOLIO_CONFIGS,
            SIGNALS_OLD, SIGNALS_NEW, MEMBERSHIP_OLD, MEMBERSHIP_NEW, PRICE_OLD, PRICE_NEW, PRICE_SUPPLEMENT,
        ]},
    }
    atomic_json(config_dir / 'protocol_lock.json', lock)

    metrics, trades = run_windows(windows, effective, membership, signals, prices, project)
    stability, horizon_champions = build_summaries(metrics, effective)
    atomic_parquet(results_dir / 'window_metrics.parquet', metrics)
    metrics.to_csv(results_dir / 'window_metrics.csv', index=False)
    atomic_parquet(results_dir / 'all_trades.parquet', trades)
    atomic_parquet(results_dir / 'strategy_horizon_stability.parquet', stability)
    stability.to_csv(results_dir / 'strategy_horizon_stability.csv', index=False)
    horizon_champions.to_csv(results_dir / 'horizon_champions.csv', index=False)

    audit = completion_audit(source, effective, windows, metrics, trades, cutoff, data_audit)
    report = write_report(project, cutoff, source, effective, windows, metrics, stability, horizon_champions, trades, audit)
    audit['runtime_seconds'] = time.time() - started
    output_paths = [
        config_dir / 'protocol_lock.json', derived_dir / 'source_strategy_union.parquet',
        derived_dir / 'effective_strategy_union.parquet', derived_dir / 'windows.parquet',
        derived_dir / 'selected_entry_signals_enriched_to_latest.parquet',
        results_dir / 'window_metrics.parquet', results_dir / 'all_trades.parquet',
        results_dir / 'strategy_horizon_stability.parquet', results_dir / 'horizon_champions.csv', report,
    ]
    audit['output_sha256'] = {str(path): sha256_file(path) for path in output_paths}
    atomic_json(reports_dir / 'completion_audit.json', audit)
    manifest = {
        'status': 'complete', 'data_cutoff': str(cutoff.date()),
        'files': {str(path): sha256_file(path) for path in output_paths + [reports_dir / 'completion_audit.json']},
    }
    atomic_json(config_dir / 'final_manifest.json', manifest)
    atomic_json(checkpoint, {
        'state': 'complete', 'data_cutoff': str(cutoff.date()),
        'runtime_seconds': audit['runtime_seconds'], 'updated_at_epoch': time.time(),
    })
    print(json.dumps({
        'status': 'complete', 'data_cutoff': str(cutoff.date()),
        'source_strategies': len(source), 'effective_strategies': len(effective),
        'windows': len(windows), 'strategy_window_results': len(metrics),
        'report': str(report), 'runtime_seconds': audit['runtime_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
