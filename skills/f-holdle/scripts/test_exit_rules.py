"""固定 -40% 硬止损、历史单确认与官网双确认止盈的最小回归测试。"""

import pandas as pd

from unified_backtest_v2 import simulate_exit


def make_weekly(rows):
    df = pd.DataFrame(rows, columns=['week_end', 'high', 'low', 'close', 'macd_sign'])
    df['week_end'] = pd.to_datetime(df['week_end'])
    return df


def test_fixed_stop_never_moves_up():
    weekly = make_weekly([
        ('2024-01-05', 140.0, 100.0, 135.0, '红'),
        ('2024-01-12', 105.0, 65.0, 65.0, '红'),
    ])
    result = simulate_exit(weekly, 100.0, pd.Timestamp('2024-01-02'))
    assert result['status'] == 'holding'
    assert result['stop_loss'] == 60.0


def test_fixed_stop_forces_exit_at_minus_40():
    weekly = make_weekly([
        ('2024-01-05', 140.0, 100.0, 135.0, '红'),
        # 盘中触及止损但周收盘重新站上止损线，仍必须强制退出。
        ('2024-01-12', 75.0, 59.0, 70.0, '红'),
    ])
    result = simulate_exit(weekly, 100.0, pd.Timestamp('2024-01-02'))
    assert result['status'] == 'sold_stop_loss'
    assert result['exit_reason'] == 'fixed_cost_stop'
    assert result['stop_loss'] == 60.0
    assert result['exit_price'] == 60.0
    assert result['return_pct'] == -40.0


def test_daily_data_sets_exact_forced_stop_date():
    weekly = make_weekly([
        ('2024-01-05', 75.0, 59.0, 70.0, '红'),
    ])
    weekly['week_start'] = pd.to_datetime(['2024-01-01'])
    daily = pd.DataFrame({
        'date': pd.to_datetime(['2024-01-02', '2024-01-03', '2024-01-04']),
        'low': [95.0, 59.0, 65.0],
    })
    result = simulate_exit(
        weekly,
        100.0,
        pd.Timestamp('2024-01-02'),
        daily=daily,
    )
    assert result['exit_date'] == pd.Timestamp('2024-01-03')
    assert result['return_pct'] == -40.0


def test_weekly_low_alone_exits_even_if_close_recovers():
    weekly = make_weekly([
        ('2024-01-05', 110.0, 101.0, 108.0, '红'),
        ('2024-01-12', 108.0, 102.0, 104.0, '绿'),
        ('2024-01-19', 115.0, 103.0, 112.0, '红'),
        # 最低价跌破 101 安全线，但周收盘重新站上；仍应退出。
        ('2024-01-26', 113.0, 99.0, 102.0, '绿'),
    ])
    result = simulate_exit(weekly, 100.0, pd.Timestamp('2024-01-02'))
    assert result['status'] == 'sold_weekly'
    assert result['exit_reason'] == 'weekly_low'
    assert result['safety_line'] == 101.0
    assert result['exit_price'] == 102.0


def test_website_three_stage_stop_reaches_breakeven():
    weekly = make_weekly([
        ('2024-01-05', 131.0, 95.0, 125.0, '红'),
        ('2024-01-12', 128.0, 99.0, 105.0, '红'),
    ])
    result = simulate_exit(
        weekly,
        100.0,
        pd.Timestamp('2024-01-02'),
        exit_mode='website',
    )
    assert result['status'] == 'sold_stop_loss'
    assert result['exit_reason'] == 'website_tiered_stop'
    assert result['stop_loss'] == 100.0
    assert result['return_pct'] == 0.0


def test_website_profit_requires_weekly_close_confirmation_with_fixed_stop():
    weekly = make_weekly([
        ('2024-01-05', 110.0, 101.0, 108.0, '红'),
        ('2024-01-12', 108.0, 102.0, 104.0, '绿'),
        ('2024-01-19', 115.0, 103.0, 112.0, '红'),
        # 周内跌破安全线但收盘收回，不卖。
        ('2024-01-26', 113.0, 99.0, 102.0, '绿'),
        # 下一周最低价与收盘均跌破，按周收盘卖出。
        ('2024-02-02', 103.0, 98.0, 99.0, '绿'),
    ])
    result = simulate_exit(
        weekly,
        100.0,
        pd.Timestamp('2024-01-02'),
        exit_mode='website_profit',
    )
    assert result['status'] == 'sold_weekly'
    assert result['exit_date'] == pd.Timestamp('2024-02-02')
    assert result['exit_price'] == 99.0
    assert result['exit_reason'] == 'weekly_low_close_confirmed'


def test_website_profit_keeps_minus_40_forced_stop():
    weekly = make_weekly([
        ('2024-01-05', 105.0, 59.0, 70.0, '红'),
    ])
    result = simulate_exit(
        weekly,
        100.0,
        pd.Timestamp('2024-01-02'),
        exit_mode='website_profit',
    )
    assert result['exit_reason'] == 'fixed_cost_stop'
    assert result['exit_price'] == 60.0
    assert result['return_pct'] == -40.0


if __name__ == '__main__':
    test_fixed_stop_never_moves_up()
    test_fixed_stop_forces_exit_at_minus_40()
    test_daily_data_sets_exact_forced_stop_date()
    test_weekly_low_alone_exits_even_if_close_recovers()
    test_website_three_stage_stop_reaches_breakeven()
    test_website_profit_requires_weekly_close_confirmation_with_fixed_stop()
    test_website_profit_keeps_minus_40_forced_stop()
    print('exit rule tests: PASS')
