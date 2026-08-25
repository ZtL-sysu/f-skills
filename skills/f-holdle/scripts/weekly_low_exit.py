"""
HOLDLE 周K低点动态出场规则计算器

输入：个股日K DataFrame（含 date/open/high/low/close/adj_close）
输出：每周状态、有效低点、安全线、卖出信号

用法示例：
    df = load_daily_data('605499.SH')
    result = weekly_low_exit(df, entry_price=240.90, entry_date='2024-06-13')
    print(result[['week_end','close','macd_sign','effective_low','safety_line','signal']])
"""

import pandas as pd
import numpy as np


def compute_weekly(df: pd.DataFrame, price_col: str = 'adj_close') -> pd.DataFrame:
    """把日K聚合为周K，并计算 MACD（12,26,9）。"""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['week'] = df['date'].dt.to_period('W-FRI')

    weekly = df.groupby('week').agg(
        week_start=('date', 'first'),
        week_end=('date', 'last'),
        open=('open', 'first'),
        high=('high', 'max'),
        low=('low', 'min'),
        close=('close', 'last'),
        adj_open=('adj_open', 'first') if 'adj_open' in df.columns else ('open', 'first'),
        adj_high=('adj_high', 'max') if 'adj_high' in df.columns else ('high', 'max'),
        adj_low=('adj_low', 'min') if 'adj_low' in df.columns else ('low', 'min'),
        adj_close=(price_col, 'last'),
    ).reset_index(drop=True)

    # MACD
    ema12 = weekly['adj_close'].ewm(span=12, adjust=False).mean()
    ema26 = weekly['adj_close'].ewm(span=26, adjust=False).mean()
    weekly['dif'] = ema12 - ema26
    weekly['dea'] = weekly['dif'].ewm(span=9, adjust=False).mean()
    weekly['macd'] = 2 * (weekly['dif'] - weekly['dea'])
    weekly['macd_sign'] = np.where(weekly['macd'] >= 0, '红', '绿')

    return weekly


def weekly_low_exit(
    df: pd.DataFrame,
    entry_price: float,
    entry_date: str,
    stop_loss_pct: float = 0.40,
    price_col: str = 'adj_close',
    require_close_confirmation: bool = True,
) -> pd.DataFrame:
    """
    计算从 entry_date 买入后的周K低点动态出场过程。

    参数：
        df: 日K DataFrame，至少包含 date/open/high/low/close/adj_close
        entry_price: 入场价（后复权口径）
        entry_date: 入场日期，'YYYY-MM-DD'
        stop_loss_pct: 初始止损比例，默认 0.40 即 40%（用户自定义）
        price_col: 用于计算 MACD 的价格列
        require_close_confirmation: 默认 True，按官网东鹏实际案例要求周收盘确认

    返回：
        weekly DataFrame，新增列：
        - effective_low: 当前循环的有效低点
        - safety_line: 当前安全线
        - signal: '' / 'switch_to_weekly' / 'sell'
        - stop_loss: 固定成本 -40% 硬止损线
    """
    weekly = compute_weekly(df, price_col=price_col)
    weekly['date'] = weekly['week_end']
    weekly = weekly[weekly['date'] >= pd.to_datetime(entry_date)].copy()

    if weekly.empty:
        raise ValueError('入场日期后无数据')

    # 初始化
    safety_line = None
    switched = False
    stop_loss = entry_price * (1 - stop_loss_pct)
    effective_low = None
    prior_high = None
    in_pullback = False

    signals = []
    lows = []
    safeties = []
    stops = []

    for i, row in weekly.iterrows():
        close = row['adj_close']
        high = row['adj_high']
        low = row['adj_low']
        prev_sign = weekly.loc[i - 1, 'macd_sign'] if i > weekly.index[0] else None
        curr_sign = row['macd_sign']

        # 用户最终口径：固定成本 -40%，不随峰值上移。
        stop_loss = entry_price * (1 - stop_loss_pct)

        signal = ''

        # 检测绿柱开始（红柱 -> 绿柱）
        if prev_sign == '红' and curr_sign == '绿':
            prior_high = weekly.loc[i - 1, 'adj_high']  # 绿柱前一周的高点 = 前高
            in_pullback = True

        # 在回撤中，突破前高
        if in_pullback and prior_high is not None and high > prior_high:
            new_high = high
            # 有效低点 = 前高与新高之间的最低价
            mask = (weekly['date'] >= weekly.loc[weekly['adj_high'] == prior_high, 'date'].iloc[-1]) & \
                   (weekly['date'] <= row['date'])
            effective_low = weekly.loc[mask, 'adj_low'].min()

            # 判断是否切换
            if not switched and effective_low > entry_price:
                switched = True
                safety_line = effective_low
                signal = 'switch_to_weekly'
            elif switched:
                # 安全线只上不下
                if effective_low > safety_line:
                    safety_line = effective_low

            in_pullback = False
            prior_high = new_high  # 新高成为下一次的前高

        # 当前官网案例口径：周最低价跌破且周收盘也低于安全线。
        if (
            switched and safety_line is not None and low < safety_line
            and (not require_close_confirmation or close < safety_line)
        ):
            signal = 'sell'

        # 如果没切换，固定成本 -40% 强制止损
        if not switched and low <= stop_loss:
            signal = 'sell_stop_loss'

        lows.append(effective_low)
        safeties.append(safety_line)
        stops.append(stop_loss)
        signals.append(signal)

    weekly['effective_low'] = lows
    weekly['safety_line'] = safeties
    weekly['stop_loss'] = stops
    weekly['signal'] = signals

    return weekly


if __name__ == '__main__':
    # 示例：构造一段假数据，演示流程
    dates = pd.date_range('2024-01-01', '2026-12-31', freq='B')
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
    df = pd.DataFrame({
        'date': dates,
        'open': prices * 0.99,
        'high': prices * 1.02,
        'low': prices * 0.98,
        'close': prices,
        'adj_close': prices,
    })

    result = weekly_low_exit(df, entry_price=100, entry_date='2024-03-01')
    print(result[['week_end', 'adj_close', 'macd_sign', 'effective_low', 'safety_line', 'stop_loss', 'signal']].tail(30))
