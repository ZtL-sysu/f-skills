"""
HOLDLE 三 A 股统一回测（官网开窗状态机 + 次月检查日K）

买入规则（来自 01_原始资料/05_第3章_择时篇.md）：
- 开窗事件：绿转红，或红柱缩短后的第一根矮转高
- 硬闸：状态A、柱≥0.5、柱≤DEA、至少30根月K
- 次月检查日K；若次月首日已是绿柱，回溯该连续绿柱段起点
- 开窗月首日至绿柱起点的最高价 = 入场参考价
- 盘中最高价严格突破参考价 → 买入，不等收盘
- 从绿柱确认后计60个交易日仍不突破 → 入场失效
- 次月柱变矮或状态A失效 → 未入场窗口关闭

卖出规则（用户硬止损 + 官网三案例止盈）：
- 未进入盈利保护前，固定成本价 -40% 强制止损，不随峰值上移
- 有效周K低点高于入场价后，按模式切换到单确认或官网双确认周K止盈
- 固定止损盘中触线即强制执行；周K止盈以周最低价跌破安全线单条件触发

仓位规则：每只股票单仓位，持仓期间跳过新窗口
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np


def load_baostock(path: str) -> pd.DataFrame:
    rows = json.loads(Path(path).read_text())
    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    for col in ['open', 'high', 'low', 'close']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    return dif, dea, 2 * (dif - dea)


def resample_monthly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['month'] = df['date'].dt.to_period('M')
    monthly = df.groupby('month', as_index=False).agg(
        month=('month', 'first'),
        month_start=('date', 'first'),
        month_end=('date', 'last'),
        open=('open', 'first'),
        high=('high', 'max'),
        low=('low', 'min'),
        close=('close', 'last'),
    ).reset_index(drop=True)
    monthly['dif'], monthly['dea'], monthly['macd'] = macd(monthly['close'])
    monthly['macd_sign'] = np.where(monthly['macd'] >= 0, '红', '绿')
    monthly['status_a'] = (monthly['dif'] >= 0) & (monthly['dea'] >= 0) & (monthly['macd'] >= 0)
    monthly['month_count'] = np.arange(1, len(monthly) + 1)

    return monthly


def resample_weekly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['week'] = df['date'].dt.to_period('W-FRI')
    weekly = df.groupby('week').agg(
        week_start=('date', 'first'),
        week_end=('date', 'last'),
        open=('open', 'first'),
        high=('high', 'max'),
        low=('low', 'min'),
        close=('close', 'last'),
    ).reset_index(drop=True)
    weekly['dif'], weekly['dea'], weekly['macd'] = macd(weekly['close'])
    weekly['macd_sign'] = np.where(weekly['macd'] >= 0, '红', '绿')
    return weekly


def detect_windows(monthly: pd.DataFrame) -> pd.DataFrame:
    m = monthly.copy()
    m['prev_macd'] = m['macd'].shift(1)
    m['prev2_macd'] = m['macd'].shift(2)
    m['prev_sign'] = m['macd_sign'].shift(1)
    m['prev_status_a'] = m['status_a'].shift(1).fillna(False).astype(bool)
    m['green_to_red'] = (m['macd_sign'] == '红') & (m['prev_sign'] == '绿')
    # “矮转高”只认红柱缩短后的第一根反转柱；连续变高不重复开窗。
    m['higher_bar'] = (
        (m['macd_sign'] == '红') &
        (m['prev_sign'] == '红') &
        m['prev_status_a'] &
        (m['macd'] > m['prev_macd']) &
        (m['prev_macd'] <= m['prev2_macd'])
    )
    m['window_event'] = m['green_to_red'] | m['higher_bar']

    # 最新官网案例的统一开窗硬闸：柱不能贴近 0 轴，且柱不得高于 DEA。
    m['away_from_zero'] = m['macd'] >= 0.5
    m['bar_below_dea'] = m['macd'] <= m['dea']
    m['enough_monthly_history'] = m.get(
        'month_count', pd.Series(np.arange(1, len(m) + 1), index=m.index)
    ) >= 30
    m['window'] = (
        m['window_event'] &
        m['status_a'] &
        m['away_from_zero'] &
        m['bar_below_dea'] &
        m['enough_monthly_history']
    )
    return m


def compute_daily_macd(daily: pd.DataFrame) -> pd.DataFrame:
    d = daily.copy().sort_values('date').reset_index(drop=True)
    d['dif'], d['dea'], d['macd'] = macd(d['close'])
    d['macd_sign'] = np.where(d['macd'] >= 0, '红', '绿')
    return d


def find_entry(
    daily: pd.DataFrame,
    next_month_start: pd.Timestamp,
    window_start: pd.Timestamp = None,
    valid_until: pd.Timestamp = None,
    max_wait: int = 60,
) -> dict:
    """按官网案例口径寻找入场点。

    到次月才检查日K；若次月首日已经处在一段绿柱中，回溯该绿柱段在
    开窗月内的起点。参考价取开窗月首日至绿柱起点的最高价；失效计时
    从绿柱确认后开始，最多等待 ``max_wait`` 个交易日突破。
    """
    daily_macd = compute_daily_macd(daily)
    next_month_start = pd.to_datetime(next_month_start)
    window_start = pd.to_datetime(window_start if window_start is not None else next_month_start)
    valid_until = pd.to_datetime(valid_until) if valid_until is not None else None
    daily_macd['prev_sign'] = daily_macd['macd_sign'].shift(1)

    eligible = daily_macd[daily_macd['date'] >= next_month_start].copy()
    if valid_until is not None:
        eligible = eligible[eligible['date'] <= valid_until]
    if eligible.empty:
        return {'status': 'no_next_month_data'}

    first_next_idx = eligible.index[0]
    green_bar_date = None

    # 次月首日若已是绿柱，识别它所属绿柱段的真正起点。
    if daily_macd.loc[first_next_idx, 'macd_sign'] == '绿':
        run_start_idx = first_next_idx
        while run_start_idx > 0 and daily_macd.loc[run_start_idx - 1, 'macd_sign'] == '绿':
            run_start_idx -= 1
        run_start_date = daily_macd.loc[run_start_idx, 'date']
        if run_start_date >= window_start:
            green_bar_date = run_start_date

    # 次月首日不是有效的持续绿柱时，等待次月首次红转绿。
    if green_bar_date is None:
        green = eligible[
            (eligible['macd_sign'] == '绿') &
            (eligible['prev_sign'] == '红')
        ]
        if green.empty:
            return {
                'status': 'no_daily_green_bar',
                'window_end_date': valid_until if valid_until is not None else eligible.iloc[-1]['date'],
            }
        green_bar_date = green.iloc[0]['date']

    # 入场参考价 = 开窗月第1个交易日 ~ 绿柱起点之间的最高价。
    ref_mask = (daily['date'] >= window_start) & (daily['date'] <= green_bar_date)
    ref_period = daily[ref_mask]
    if ref_period.empty:
        return {'status': 'empty_ref_period'}
    reference_price = ref_period['high'].max()

    # 失效计时从绿柱确认后开始；实际买入不得早于次月。
    post_green = daily_macd[daily_macd['date'] > green_bar_date].head(max_wait).copy()
    if valid_until is not None:
        post_green = post_green[post_green['date'] <= valid_until]
    candidates = post_green[post_green['date'] >= next_month_start]
    breakout = candidates[candidates['high'] > reference_price]
    if breakout.empty:
        if not post_green.empty:
            window_end_date = post_green.iloc[-1]['date']
        elif valid_until is not None:
            window_end_date = valid_until
        else:
            window_end_date = green_bar_date
        return {
            'status': 'no_breakout',
            'reference_price': reference_price,
            'green_bar_date': green_bar_date,
            'window_end_date': window_end_date,
        }

    entry = breakout.iloc[0]
    return {
        'status': 'entered',
        'entry_date': entry['date'],
        'entry_price': reference_price,
        'green_bar_date': green_bar_date,
        'reference_price': reference_price,
        'breakout_high': entry['high'],
        'window_end_date': entry['date'],
    }


def monthly_window_valid_until(monthly: pd.DataFrame, window_idx: int) -> pd.Timestamp:
    """返回未入场窗口的月线关闭日。

    开窗次月柱变矮时于次月末关闭；若其后状态A先失效，则在失效月末关闭。
    返回 ``None`` 表示月线层面尚未关闭，最终仍受绿柱后60个交易日约束。
    """
    position = monthly.index.get_loc(window_idx)
    row = monthly.loc[window_idx]
    cutoffs = []

    if position + 1 < len(monthly):
        next_row = monthly.iloc[position + 1]
        if next_row['macd'] < row['macd']:
            cutoffs.append(pd.to_datetime(next_row['month_end']))

    later = monthly.iloc[position + 1:]
    failed = later[~later['status_a']]
    if not failed.empty:
        cutoffs.append(pd.to_datetime(failed.iloc[0]['month_end']))

    return min(cutoffs) if cutoffs else None


def simulate_exit(
    weekly: pd.DataFrame,
    entry_price: float,
    entry_date: pd.Timestamp,
    end_date: pd.Timestamp = None,
    initial_stop_pct: float = 0.40,
    daily: pd.DataFrame = None,
    exit_mode: str = 'current',
) -> dict:
    """执行当前用户版、网站三阶止损版或用户固定止损+官网止盈版。

    ``current`` 使用固定成本 -40% 强制止损；``website`` 使用网站
    三阶止损（-20% / 峰值达 +20% 后 -10% / 峰值达 +30% 后保本）。
    ``website_profit`` 保留固定成本 -40% 强制止损，但按东鹏饮料官网
    实际案例要求周K最低价与周收盘均跌破安全线才止盈。形成高于成本
    的有效周K低点后，三种模式都切换到周K保护模式。
    """
    if exit_mode not in {'current', 'website', 'website_profit'}:
        raise ValueError(f'unsupported exit_mode: {exit_mode}')
    weekly_all = weekly.sort_values('week_end').reset_index(drop=True)
    eligible_idx = weekly_all.index[weekly_all['week_end'] >= pd.to_datetime(entry_date)]
    pre_entry_sign = None
    if len(eligible_idx) > 0 and eligible_idx[0] > 0:
        pre_entry_sign = weekly_all.loc[eligible_idx[0] - 1, 'macd_sign']
    weekly = weekly_all[weekly_all['week_end'] >= pd.to_datetime(entry_date)].copy()
    if end_date is not None:
        weekly = weekly[weekly['week_end'] <= pd.to_datetime(end_date)].copy()
    weekly = weekly.reset_index(drop=True)
    daily_after_entry = None
    if daily is not None and not daily.empty:
        daily_after_entry = daily.copy()
        daily_after_entry['date'] = pd.to_datetime(daily_after_entry['date'])
        daily_after_entry = daily_after_entry[
            daily_after_entry['date'] >= pd.to_datetime(entry_date)
        ].sort_values('date')
        if end_date is not None:
            daily_after_entry = daily_after_entry[
                daily_after_entry['date'] <= pd.to_datetime(end_date)
            ]
    if weekly.empty:
        return {'status': 'no_weekly_data'}

    safety_line = None
    switched = False
    fixed_stop_mode = exit_mode in {'current', 'website_profit'}
    stop_loss = entry_price * (1 - initial_stop_pct) if fixed_stop_mode else entry_price * 0.80
    peak_price = entry_price
    prior_high = None
    prior_high_idx = None
    effective_low = None
    state = 'riding'
    cycle_start_idx = 0

    for i, row in weekly.iterrows():
        close = row['close']
        high = row['high']
        low = row['low']
        prev_sign = weekly.loc[i - 1, 'macd_sign'] if i > 0 else pre_entry_sign
        curr_sign = row['macd_sign']

        if fixed_stop_mode:
            stop_loss = entry_price * (1 - initial_stop_pct)
        elif peak_price >= entry_price * 1.30:
            stop_loss = entry_price
        elif peak_price >= entry_price * 1.20:
            stop_loss = entry_price * 0.90
        else:
            stop_loss = entry_price * 0.80

        # 固定硬止损用日K定位真实触发日；盈利保护的周K切换只在周末确认。
        if not switched and daily_after_entry is not None:
            week_days = daily_after_entry[
                (daily_after_entry['date'] >= row['week_start']) &
                (daily_after_entry['date'] <= row['week_end'])
            ]
            for _, day in week_days.iterrows():
                # 日线无法判断同日高低价的盘中先后；先执行前一日已确认的
                # 止损，再按当日最高价升级下一交易日起生效的三阶止损。
                if day['low'] <= stop_loss:
                    reason = 'fixed_cost_stop' if fixed_stop_mode else 'website_tiered_stop'
                    return {
                        'status': 'sold_stop_loss',
                        'exit_date': day['date'],
                        'exit_price': stop_loss,
                        'stop_loss': stop_loss,
                        'exit_reason': reason,
                        'return_pct': (stop_loss - entry_price) / entry_price * 100,
                    }
                if exit_mode == 'website':
                    peak_price = max(peak_price, day['high'])
                    if peak_price >= entry_price * 1.30:
                        stop_loss = entry_price
                    elif peak_price >= entry_price * 1.20:
                        stop_loss = entry_price * 0.90

        # 周K绿柱开始新周期
        if prev_sign == '红' and curr_sign == '绿':
            high_slice = weekly.loc[cycle_start_idx:i - 1, 'high']
            if high_slice.empty:
                high_slice = weekly.loc[i:i, 'high']
            prior_high_idx = high_slice.idxmax()
            prior_high = weekly.loc[prior_high_idx, 'high']
            state = 'pullback'

        # 回撤中突破前高
        if state == 'pullback' and prior_high is not None and high > prior_high:
            new_high = high
            effective_low = weekly.loc[prior_high_idx:i, 'low'].min()

            if not switched and effective_low > entry_price:
                switched = True
                safety_line = effective_low
            elif switched and effective_low > safety_line:
                safety_line = effective_low

            state = 'riding'
            cycle_start_idx = i
            prior_high = new_high
            prior_high_idx = i

        # current 为冻结的“周最低价单确认”基线；website_profit 严格采用
        # 东鹏官网实际案例的“周最低价跌破 + 周收盘确认”双确认。
        weekly_breach = switched and safety_line is not None and low < safety_line
        close_confirmed = weekly_breach and close < safety_line
        if weekly_breach and (exit_mode != 'website_profit' or close_confirmed):
            return {
                'status': 'sold_weekly',
                'exit_date': row['week_end'],
                'exit_price': close,
                'safety_line': safety_line,
                'exit_reason': 'weekly_low_close_confirmed' if exit_mode == 'website_profit' else 'weekly_low',
                'return_pct': (close - entry_price) / entry_price * 100,
            }

        # 固定 -40% 是强制止损：周内最低价触线即按止损线成交，不等待周收盘。
        if not switched and daily_after_entry is None and low <= stop_loss:
            reason = 'fixed_cost_stop' if fixed_stop_mode else 'website_tiered_stop'
            return {
                'status': 'sold_stop_loss',
                'exit_date': row['week_end'],
                'exit_price': stop_loss,
                'stop_loss': stop_loss,
                'exit_reason': reason,
                'return_pct': (stop_loss - entry_price) / entry_price * 100,
            }

        if exit_mode == 'website' and daily_after_entry is None:
            peak_price = max(peak_price, high)

    last = weekly.iloc[-1]
    return {
        'status': 'holding',
        'last_date': last['week_end'],
        'last_price': last['close'],
        'safety_line': safety_line,
        'stop_loss': stop_loss if not switched else None,
        'exit_reason': '',
        'return_pct': (last['close'] - entry_price) / entry_price * 100,
    }


def backtest_stock(name: str, code: str, data_path: str, focus_windows: list = None) -> list:
    """对单只股票做严格单仓位回测。"""
    print(f'\n========== {name} ({code}) ==========')

    daily = load_baostock(data_path)
    monthly = detect_windows(resample_monthly(daily))
    weekly = resample_weekly(daily)

    # 开窗条件已经包含官网案例的状态A、贴0轴、柱≤DEA与样本期硬闸。
    windows = monthly[monthly['window']].copy()

    trades = []
    holding = False
    entry_date = None
    exit_date = None
    window_blocked_until = None

    for _, window in windows.iterrows():
        window_start = window['month_start']
        window_end = window['month_end']
        window_label = window_end.strftime('%Y-%m')

        # 一个窗口存活期间，后续柱体波动不重复开窗。
        if window_blocked_until is not None and window_start <= window_blocked_until:
            continue

        # 只测指定的重点窗口（如果有）
        if focus_windows and window_label not in focus_windows:
            continue

        # 单仓位：即使回测已知未来退出日，也必须跳过真实持仓区间内的新窗口。
        if exit_date is not None and window_start <= exit_date:
            continue
        if exit_date is not None and window_start > exit_date:
            holding = False

        # 状态 A 确认后，次月切换日 K
        signal_month = window['month']
        next_month = signal_month + 1
        next_month_mask = daily['date'].dt.to_period('M') == next_month
        if not next_month_mask.any():
            continue
        next_month_start = daily.loc[next_month_mask, 'date'].min()

        valid_until = monthly_window_valid_until(monthly, window.name)
        entry = find_entry(
            daily,
            next_month_start,
            window_start=window_start,
            valid_until=valid_until,
        )
        if entry['status'] != 'entered':
            window_blocked_until = entry.get('window_end_date', valid_until)
            continue

        entry_date = entry['entry_date']
        entry_price = entry['entry_price']
        window_blocked_until = entry_date
        holding = True

        exit_result = simulate_exit(weekly, entry_price, entry_date, daily=daily)
        exit_date = exit_result.get('exit_date', exit_result.get('last_date'))

        trade = {
            'name': name,
            'code': code,
            'window_month': window_label,
            'entry_date': entry_date,
            'entry_price': entry_price,
            'green_bar_date': entry['green_bar_date'],
            'reference_price': entry['reference_price'],
            **exit_result,
        }
        trades.append(trade)

        if exit_result['status'] == 'holding':
            holding = True
        else:
            holding = False

    return trades


def main():
    # 保留旧行情样本的读取位置；所有新回测产物统一写入训练记录目录。
    holdle_root = Path(os.environ.get('HOLDLE_ROOT', Path.home() / 'code/holdle')).expanduser()
    input_dir = Path(os.environ.get('HOLDLE_INPUT_DIR', holdle_root / 'gj')).expanduser()
    output_dir = Path(os.environ.get('HOLDLE_OUTPUT_ROOT', holdle_root / '04_训练记录')).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 分别回测三只股票的重点窗口
    all_trades = []

    # 东鹏：重点 2024-05 窗口（网站主案例）
    all_trades.extend(backtest_stock(
        '东鹏饮料', '605499.SH', str(input_dir / 'sh_605499_baostock_badj.json'),
        focus_windows=['2024-05']
    ))

    # 美的：网站列出的三个窗口 + 规则自动选的 2016-06
    all_trades.extend(backtest_stock(
        '美的集团', '000333.SZ', str(input_dir / 'sz_000333_baostock_badj.json'),
        focus_windows=['2016-06', '2017-02', '2019-07', '2020-06']
    ))

    # 药明康德：重点 2026-06 窗口
    all_trades.extend(backtest_stock(
        '药明康德', '603259.SH', str(input_dir / 'sh_603259_baostock_badj.json'),
        focus_windows=['2026-06']
    ))

    # 汇总
    summary = []
    for t in all_trades:
        exit_date = t.get('exit_date', t.get('last_date'))
        exit_price = t.get('exit_price', t.get('last_price'))
        summary.append({
            'name': t['name'],
            'code': t['code'],
            'window_month': t['window_month'],
            'entry_date': t['entry_date'].strftime('%Y-%m-%d'),
            'entry_price': round(t['entry_price'], 2),
            'green_bar_date': t['green_bar_date'].strftime('%Y-%m-%d'),
            'reference_price': round(t['reference_price'], 2),
            'exit_status': t['status'],
            'exit_date': exit_date.strftime('%Y-%m-%d'),
            'exit_price': round(exit_price, 2),
            'return_pct': round(t['return_pct'], 2),
        })

    df = pd.DataFrame(summary)
    print('\n\n========== 统一回测汇总（v2）==========')
    print(df.to_string(index=False))

    out = output_dir / 'unified_backtest_v2_summary.csv'
    df.to_csv(out, index=False, encoding='utf-8-sig')
    print(f'\n已保存: {out}')


if __name__ == '__main__':
    main()
