"""官网买入状态机与三只 A 股案例的回归测试。"""

import os
from pathlib import Path

import pandas as pd

from unified_backtest_v2 import (
    detect_windows,
    find_entry,
    load_baostock,
    monthly_window_valid_until,
    resample_monthly,
)


HOLDLE_ROOT = Path(os.environ.get('HOLDLE_ROOT', Path.home() / 'code/holdle')).expanduser()
FIXTURE_DIR = Path(os.environ.get('HOLDLE_FIXTURE_DIR', HOLDLE_ROOT / 'gj')).expanduser()


def make_monthly(macd_values, dea_values, signs, statuses):
    count = len(macd_values)
    return pd.DataFrame({
        'month': pd.period_range('2020-01', periods=count, freq='M'),
        'month_start': pd.date_range('2020-01-01', periods=count, freq='MS'),
        'month_end': pd.date_range('2020-01-31', periods=count, freq='ME'),
        'macd': macd_values,
        'dea': dea_values,
        'macd_sign': signs,
        'status_a': statuses,
        'month_count': range(1, count + 1),
    })


def test_opening_hard_gates_and_first_turn_only():
    # 前 30 个月仅用于满足官网案例的最少月K样本要求。
    macd_values = [-1.0] * 30 + [0.28, -1.0, 2.0, 3.0, 2.0, 2.5]
    dea_values = [5.0] * 32 + [1.0, 5.0, 5.0, 5.0]
    signs = ['绿'] * 30 + ['红', '绿', '红', '红', '红', '红']
    statuses = [False] * 30 + [True, False, True, True, True, True]
    result = detect_windows(make_monthly(macd_values, dea_values, signs, statuses))

    assert not result.iloc[30]['window']  # 柱 0.28，贴近0轴，降级。
    assert not result.iloc[32]['window']  # 柱 2.0 > DEA 1.0，硬闸否决。
    assert not result.iloc[33]['higher_bar']  # 连续变高不重复开窗。
    assert result.iloc[35]['higher_bar']  # 3.0→2.0→2.5，首根矮转高。
    assert result.iloc[35]['window']


def evaluate_case(path: Path, label: str):
    daily = load_baostock(str(path))
    monthly = detect_windows(resample_monthly(daily))
    row = monthly[monthly['month'].astype(str) == label].iloc[0]
    next_month = row['month'] + 1
    next_month_start = daily.loc[
        daily['date'].dt.to_period('M') == next_month, 'date'
    ].min()
    valid_until = monthly_window_valid_until(monthly, row.name)
    result = find_entry(
        daily,
        next_month_start,
        window_start=row['month_start'],
        valid_until=valid_until,
    )
    return row, result


def test_three_a_share_case_entries_match_website():
    fixtures = {
        'dongpeng': FIXTURE_DIR / 'sh_605499_baostock_badj.json',
        'wuxi': FIXTURE_DIR / 'sh_603259_baostock_badj.json',
        'midea': FIXTURE_DIR / 'sz_000333_baostock_badj.json',
    }
    if not all(path.exists() for path in fixtures.values()):
        return

    row, dongpeng = evaluate_case(fixtures['dongpeng'], '2024-05')
    assert row['window']
    assert dongpeng['green_bar_date'] == pd.Timestamp('2024-05-20')
    assert round(dongpeng['reference_price'], 2) == 241.17
    assert dongpeng['entry_date'] == pd.Timestamp('2024-06-13')

    row, wuxi = evaluate_case(fixtures['wuxi'], '2026-06')
    assert row['window']
    assert wuxi['green_bar_date'] == pd.Timestamp('2026-07-13')
    assert round(wuxi['reference_price'], 2) == 333.90
    assert wuxi['entry_date'] == pd.Timestamp('2026-07-15')

    row, midea_failed = evaluate_case(fixtures['midea'], '2016-06')
    assert row['window']
    assert midea_failed['status'] == 'no_breakout'
    assert round(midea_failed['reference_price'], 2) == 123.48

    row, midea_2017 = evaluate_case(fixtures['midea'], '2017-02')
    assert row['window']
    assert round(midea_2017['reference_price'], 2) == 139.76
    assert midea_2017['entry_date'] == pd.Timestamp('2017-03-08')

    row, midea_2020 = evaluate_case(fixtures['midea'], '2020-06')
    assert row['window']
    assert round(midea_2020['reference_price'], 2) == 313.10
    assert midea_2020['entry_date'] == pd.Timestamp('2020-07-20')


if __name__ == '__main__':
    test_opening_hard_gates_and_first_turn_only()
    test_three_a_share_case_entries_match_website()
    print('entry rule tests: PASS')
