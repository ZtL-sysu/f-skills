"""
HOLDLE 2020-2026 A 股全量回测（官网金字塔 + 固定 -40% 硬止损 + 用户定制周K止盈）

优化规则：
1. 选股 ROE 按官网阈值：≥10% 合格；≥20% 稳健；≥35% 优秀。当前以 ≥10% 为硬性门槛，
   后续通过综合评分优中选优。
2. 金字塔行业过滤：在申万行业内按综合评分排名前 10% 的股票才进入候选池。
3. 综合评分：ROE 30%、净利率 20%、毛利率 20%、现金占比 15%、负债稳定 10%、EPS 5%。
4. 官网开窗状态机：绿转红/首根矮转高 + 状态A + 柱≥0.5 + 柱≤DEA + 30月样本。
5. 同一窗口只开一次；次月柱变矮或状态A失效时关闭未入场窗口。
6. 次月检查日K；识别持续绿柱段，参考价从开窗月首日开始计算。
7. 组合管理：总资金 10 万，每只股票最多 1 万，最多同时持有 10 只；
   当候选信号超过容量时，按选股综合评分择优录取。
8. 卖出：成本价 -40% 固定强制止损；盈利后周最低价跌破安全线即触发，不要求周收盘确认。

输出：
- large_scale_trades_portfolio_v8_holdle40_web_buy_low_only.csv
- annual_summary_portfolio_v8_holdle40_web_buy_low_only.csv
- portfolio_log_v8_holdle40_web_buy_low_only.csv
- large_scale_summary_portfolio_v8_holdle40_web_buy_low_only.json
"""

import json
import multiprocessing as mp
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import pymysql

CODEX_HOME = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')).expanduser()
HOLDLE_ROOT = Path(os.environ.get('HOLDLE_ROOT', Path.home() / 'code/holdle')).expanduser()
GJDATA_SCRIPTS_DIR = CODEX_HOME / 'skills/gjdata/scripts'
if str(GJDATA_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(GJDATA_SCRIPTS_DIR))
from gj_db import build_db_config

from unified_backtest_v2 import (
    detect_windows,
    find_entry,
    monthly_window_valid_until,
    resample_monthly,
    resample_weekly,
    simulate_exit,
)

warnings.filterwarnings('ignore')

DATA_DIR = Path(os.environ.get('HOLDLE_OUTPUT_ROOT', HOLDLE_ROOT / '04_训练记录')).expanduser()
EXIT_MODE = os.environ.get('HOLDLE_EXIT_MODE', 'current').strip().lower()
if EXIT_MODE not in {'current', 'website'}:
    raise ValueError('HOLDLE_EXIT_MODE must be current or website')
DEFAULT_RUN_TAG = (
    'v8_holdle40_web_buy_low_only'
    if EXIT_MODE == 'current'
    else 'v8_website_exit_web_buy_low_only'
)
RUN_TAG = os.environ.get('HOLDLE_RUN_TAG', DEFAULT_RUN_TAG)

# 2017-2019 仅用于 MACD 预热；交易统计从 2020-01-01 开始。
START_DATE = '20170101'
# 本次结果固定截至 gjdata 最新交易日，禁止读取未来数据。
END_DATE = '20260818'
BACKTEST_START = pd.Timestamp('2020-01-01')
BACKTEST_END = pd.Timestamp('2026-08-18')

# 选股参数（官网口径：ROE ≥10% 合格，≥20% 稳健，≥35% 优秀）
ROE_THRESHOLD = 10.0
ROE_BOUNDARY_LOW = 8.0
ROE_BOUNDARY_HIGH = 12.0

# 金字塔行业过滤：同行业内按综合评分排名前 10%
PYRAMID_TOP_PCT = 0.10
MIN_PYRAMID_KEEP = 1  # 行业内至少保留 1 只

# 组合参数
INITIAL_CAPITAL = 100_000.0
POSITION_SIZE = 10_000.0
MAX_POSITIONS = int(INITIAL_CAPITAL // POSITION_SIZE)


DB_CONFIG = build_db_config()


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def query(sql: str, params=None) -> pd.DataFrame:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params) if params is not None else ())
            rows = cur.fetchall()
            return pd.DataFrame(rows)


def load_stock_universe() -> pd.DataFrame:
    path = DATA_DIR / 'backtest_universe.csv'
    if path.exists():
        return pd.read_csv(path)
    sql = """
    SELECT S_INFO_WINDCODE AS code, S_INFO_CODE AS short_code,
           S_INFO_NAME AS name, S_INFO_LISTDATE AS list_date,
           S_INFO_EXCHMARKET AS exchange, S_INFO_LISTBOARDNAME AS board
    FROM AShareDescription
    WHERE S_INFO_LISTDATE IS NOT NULL
      AND S_INFO_LISTDATE < '20200101'
      AND (S_INFO_DELISTDATE IS NULL OR S_INFO_DELISTDATE = 'None')
    ORDER BY S_INFO_WINDCODE
    """
    df = query(sql)
    df['list_date'] = pd.to_datetime(df['list_date'], format='%Y%m%d', errors='coerce')
    df.to_csv(path, index=False, encoding='utf-8-sig')
    return df


def _load_financial_table(codes: List[str], table: str, columns: List[str], statement_type: str,
                          ann_col: str, cache_name: str) -> pd.DataFrame:
    """逐表读取年报数据并保留公告日，满足时间机器/无前视约束。"""
    cache = DATA_DIR / cache_name
    if cache.exists():
        cached = pd.read_parquet(cache)
        if ann_col in cached.columns:
            return cached

    all_rows = []
    batch_size = 200
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i + batch_size]
        placeholders = ','.join(['%s'] * len(batch))
        sql = f"""
        SELECT {','.join(columns)}
        FROM {table}
        WHERE S_INFO_WINDCODE IN ({placeholders})
          AND STATEMENT_TYPE = %s
          AND SUBSTRING(REPORT_PERIOD, 5, 4) = '1231'
        ORDER BY S_INFO_WINDCODE, REPORT_PERIOD, {ann_col}
        """
        all_rows.append(query(sql, batch + [statement_type]))
        print(f'  {table} {min(i + batch_size, len(codes))}/{len(codes)}', flush=True)

    df = pd.concat(all_rows, ignore_index=True)
    df['REPORT_PERIOD'] = pd.to_datetime(df['REPORT_PERIOD'], format='%Y%m%d', errors='coerce')
    df[ann_col] = pd.to_datetime(df[ann_col], format='%Y%m%d', errors='coerce')
    numeric_cols = [c for c in columns if c not in {'S_INFO_WINDCODE', 'REPORT_PERIOD', ann_col}]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.to_parquet(cache, index=False)
    return df


def load_financial_data(codes: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    fi_cols = [
        'S_INFO_WINDCODE', 'ANN_DT', 'REPORT_PERIOD', 'S_FA_ROE',
        'S_FA_GROSSPROFITMARGIN', 'S_FA_NETPROFITMARGIN', 'S_FA_ASSETSTURN',
        'S_FA_EPS_BASIC', 'S_FA_DEBTTOASSETS',
    ]
    bs_cols = [
        'S_INFO_WINDCODE', 'ACTUAL_ANN_DT', 'REPORT_PERIOD',
        'MONETARY_CAP', 'TOT_ASSETS', 'TOT_LIAB',
    ]
    fi = _load_financial_table(
        codes, 'AShareFinancialIndicator', fi_cols, '合并报表', 'ANN_DT',
        'backtest_financial_pit.parquet',
    )
    bs = _load_financial_table(
        codes, 'AShareBalanceSheet', bs_cols, '408001000', 'ACTUAL_ANN_DT',
        'backtest_balance_pit.parquet',
    )
    bs['cash_ratio'] = bs['MONETARY_CAP'] / bs['TOT_ASSETS'] * 100
    return fi, bs


def load_industry_membership() -> pd.DataFrame:
    """加载申万行业历史归属，按每年 4 月 30 日做时点还原。"""
    cache = DATA_DIR / 'sw_industry_membership_history.csv'
    if cache.exists():
        df = pd.read_csv(cache)
    else:
        sql = """
        SELECT S_INFO_WINDCODE AS code, SW_IND_CODE AS industry,
               ENTRY_DT AS entry_date, REMOVE_DT AS remove_date
        FROM AShareSWNIndustriesClass
        """
        df = query(sql)
        df.to_csv(cache, index=False, encoding='utf-8-sig')
    df['entry_date'] = pd.to_datetime(df['entry_date'], format='%Y%m%d', errors='coerce')
    df['remove_date'] = pd.to_datetime(df['remove_date'], format='%Y%m%d', errors='coerce')
    return df


def load_prices(codes: List[str], start: str, end: str) -> pd.DataFrame:
    all_rows = []
    batch_size = 50
    cols = ['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_ADJOPEN', 'S_DQ_ADJHIGH', 'S_DQ_ADJLOW', 'S_DQ_ADJCLOSE']
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i + batch_size]
        placeholders = ','.join(['%s'] * len(batch))
        sql = f"""
        SELECT {','.join(cols)}
        FROM AShareEODPrices
        WHERE S_INFO_WINDCODE IN ({placeholders})
          AND TRADE_DT BETWEEN %s AND %s
        ORDER BY S_INFO_WINDCODE, TRADE_DT
        """
        df = query(sql, batch + [start, end])
        all_rows.append(df)
    df = pd.concat(all_rows, ignore_index=True)
    df['TRADE_DT'] = pd.to_datetime(df['TRADE_DT'], format='%Y%m%d', errors='coerce')
    for c in cols[2:]:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    return df


def load_market_index() -> pd.DataFrame:
    """加载沪深300日行情，用于市场环境过滤。"""
    cache = DATA_DIR / 'csi300_daily.csv'
    if cache.exists():
        df = pd.read_csv(cache)
        df['date'] = pd.to_datetime(df['date'])
        return df
    sql = """
    SELECT TRADE_DT AS date, S_DQ_CLOSE AS close
    FROM AIndexEODPrices
    WHERE S_INFO_WINDCODE = '000300.SH'
      AND TRADE_DT BETWEEN %s AND %s
    ORDER BY TRADE_DT
    """
    df = query(sql, [START_DATE, END_DATE])
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d', errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df.to_csv(cache, index=False, encoding='utf-8-sig')
    return df


def trend_score(values: pd.Series, stable_cv: float = 0.20) -> Dict:
    values = values.dropna()
    if len(values) < 2:
        return {'trend': 'unknown', 'slope': np.nan, 'cv': np.nan, 'rel_slope': np.nan, 'stability': 'unknown'}
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    mean_v = values.mean()
    std_v = values.std()
    cv = std_v / abs(mean_v) if mean_v != 0 else np.nan
    rel_slope = slope / abs(mean_v) if mean_v != 0 else np.nan
    if rel_slope > 0.05:
        trend = 'rising'
    elif rel_slope < -0.05:
        trend = 'falling'
    else:
        trend = 'stable'
    stability = 'stable' if cv < stable_cv else ('moderate' if cv < 0.30 else 'volatile')
    return {'trend': trend, 'slope': slope, 'cv': cv, 'rel_slope': rel_slope, 'stability': stability}


def compute_selection_score(fi: pd.DataFrame, bs: pd.DataFrame, code: str,
                            ref_date: pd.Timestamp, n_years: int = 5) -> Tuple[float, bool]:
    """
    计算选股综合评分，并返回是否通过基础门槛。
    评分逻辑参考官网金字塔权重：ROE 最高，其次净利率、毛利率、现金占比、负债稳定、EPS 增长。
    """
    # 时间机器约束：只使用 ref_date 当天已经公告的数据，不能只按报告期过滤。
    f = fi[(fi['S_INFO_WINDCODE'] == code) & (fi['ANN_DT'] <= ref_date)]
    b = bs[(bs['S_INFO_WINDCODE'] == code) & (bs['ACTUAL_ANN_DT'] <= ref_date)]
    if f.empty or b.empty:
        return 0.0, False
    f = (
        f.sort_values(['REPORT_PERIOD', 'ANN_DT'])
        .drop_duplicates(subset=['REPORT_PERIOD'], keep='last')
        .tail(n_years)
    )
    b = (
        b.sort_values(['REPORT_PERIOD', 'ACTUAL_ANN_DT'])
        .drop_duplicates(subset=['REPORT_PERIOD'], keep='last')
        .tail(n_years)
    )
    if len(f) < 3:
        return 0.0, False

    roe = f['S_FA_ROE']
    roe_trend = trend_score(roe, stable_cv=0.20)
    roe_latest = roe.iloc[-1]
    roe_pass = (
        roe_latest >= ROE_THRESHOLD
        or (ROE_BOUNDARY_LOW <= roe_latest <= ROE_BOUNDARY_HIGH and roe_trend['stability'] != 'volatile')
    )

    gm = f['S_FA_GROSSPROFITMARGIN']
    gm_trend = trend_score(gm)
    gm_pass = gm.iloc[-1] >= 20 and gm_trend['stability'] != 'volatile'

    nm = f['S_FA_NETPROFITMARGIN']
    nm_trend = trend_score(nm)
    nm_pass = (
        nm.iloc[-1] >= 10
        or (nm.iloc[-1] >= 9 and nm_trend['trend'] in ('rising', 'stable'))
        or (roe_latest >= ROE_THRESHOLD and nm.iloc[-1] >= 20)
    )

    cash_avg = b['cash_ratio'].mean()
    cash_pass = cash_avg >= 10

    debt = f['S_FA_DEBTTOASSETS']
    debt_trend = trend_score(debt)
    debt_pass = not (debt_trend['trend'] == 'rising' and debt_trend['cv'] > 0.15)

    eps = f['S_FA_EPS_BASIC'].dropna()
    eps_nonzero = eps[eps != 0]
    eps_pass = False
    if len(eps_nonzero) >= 2:
        eps_growth = (eps_nonzero.iloc[-1] - eps_nonzero.iloc[0]) / abs(eps_nonzero.iloc[0]) * 100
        yoy = eps_nonzero.pct_change().dropna()
        eps_pass = (eps_growth >= 0) or (yoy.mean() >= 0 and (yoy < -0.10).sum() <= 1)

    base_pass = roe_pass and gm_pass and nm_pass and cash_pass and debt_pass and eps_pass
    if not base_pass:
        return 0.0, False

    # 综合评分（0-1000），权重参考官网金字塔
    def norm_score(value: float, target: float, cap: float = 1000.0) -> float:
        if pd.isna(value) or target <= 0:
            return 0.0
        return min(value / target * 1000.0, cap)

    roe_score = norm_score(roe_latest, 35.0)
    if roe_trend['trend'] == 'rising':
        roe_score *= 1.15
    elif roe_trend['stability'] == 'stable':
        roe_score *= 1.05

    nm_score = norm_score(nm.iloc[-1], 20.0)
    if nm_trend['trend'] == 'rising':
        nm_score *= 1.10

    gm_score = norm_score(gm.iloc[-1], 30.0)
    if gm_trend['trend'] == 'rising':
        gm_score *= 1.05

    cash_score = norm_score(cash_avg, 25.0)

    debt_score = 800.0
    if debt_trend['trend'] == 'rising':
        debt_score = max(0.0, 800.0 - debt_trend['cv'] * 2000)
    elif debt_trend['trend'] == 'falling':
        debt_score = 1000.0

    eps_score = 500.0
    if len(eps_nonzero) >= 2:
        eps_score = min(1000.0, max(0.0, 500.0 + eps_growth * 10))

    weights = {
        'roe': 0.30,
        'nm': 0.20,
        'gm': 0.20,
        'cash': 0.15,
        'debt': 0.10,
        'eps': 0.05,
    }
    total = (
        weights['roe'] * roe_score +
        weights['nm'] * nm_score +
        weights['gm'] * gm_score +
        weights['cash'] * cash_score +
        weights['debt'] * debt_score +
        weights['eps'] * eps_score
    )
    return round(total, 2), True


def build_eligibility_and_scores(fi: pd.DataFrame, bs: pd.DataFrame, codes: List[str],
                                  years: List[int],
                                  industry_membership: pd.DataFrame = None) -> Dict[str, Dict[int, Tuple[bool, float]]]:
    """
    计算全部股票的选股评分，并施加金字塔行业内排名过滤：
    每年 4 月 30 日，对每个申万三级行业内的合格股票按综合评分排序，
    只保留评分前 10%（至少 1 只）的股票进入候选池。
    """
    # 先算全部股票原始分
    raw = {}  # code -> {year: (passed, score)}
    for code in codes:
        raw[code] = {}
        for year in years:
            ref_date = pd.Timestamp(f'{year}-04-30')
            score, passed = compute_selection_score(fi, bs, code, ref_date)
            raw[code][year] = (passed, score)

    result = {code: {} for code in codes}

    if industry_membership is None or industry_membership.empty:
        # 无行业过滤：直接透传
        return raw

    for year in years:
        ref_date = pd.Timestamp(f'{year}-04-30')
        active_industry = industry_membership[
            (industry_membership['entry_date'] <= ref_date) &
            (industry_membership['remove_date'].isna() | (industry_membership['remove_date'] > ref_date))
        ].copy()
        active_industry = (
            active_industry.sort_values(['code', 'entry_date'])
            .drop_duplicates(subset=['code'], keep='last')
        )
        code_to_ind = dict(zip(active_industry['code'], active_industry['industry']))

        # 当年所有合格股票
        passed_rows = [
            (code, raw[code][year][1]) for code in codes
            if raw[code][year][0]
        ]
        # 按行业分组
        ind_groups: Dict[str, List[Tuple[str, float]]] = {}
        for code, score in passed_rows:
            ind = code_to_ind.get(code)
            if pd.isna(ind) or not ind:
                # 无行业归属的股票不进金字塔，但仍可参与（按全局排名）
                ind = '__no_industry__'
            ind_groups.setdefault(ind, []).append((code, score))

        # 行业内按评分降序，保留前 10%
        keep_codes = set()
        for ind, items in ind_groups.items():
            items_sorted = sorted(items, key=lambda x: x[1], reverse=True)
            n_keep = max(MIN_PYRAMID_KEEP, int(np.ceil(len(items_sorted) * PYRAMID_TOP_PCT)))
            keep_codes.update(c for c, _ in items_sorted[:n_keep])

        for code in codes:
            result[code][year] = (raw[code][year][0] and code in keep_codes, raw[code][year][1])

    return result


def build_market_regime(market_daily: pd.DataFrame) -> pd.DataFrame:
    """计算沪深300的月K状态A与开窗事件，供市场环境观察。
    指数数据只有收盘价，因此 open/high/low 均用 close 填充。"""
    df = market_daily.copy()
    df['open'] = df['high'] = df['low'] = df['close']
    monthly = resample_monthly(df)
    monthly = detect_windows(monthly)
    return monthly[['month', 'month_start', 'month_end', 'status_a', 'window']].copy()


def run_backtest_for_stock(code: str, name: str, daily: pd.DataFrame,
                           eligibility: Dict[int, Tuple[bool, float]],
                           market_regime: pd.DataFrame = None) -> List[Dict]:
    """生成某只股票的所有候选交易（未考虑组合资金限制）。"""
    if daily.empty or len(daily) < 100:
        return []

    daily = daily.sort_values('date').reset_index(drop=True)
    monthly = detect_windows(resample_monthly(daily))
    weekly = resample_weekly(daily)

    # 开窗条件已经包含官网案例的状态A、贴0轴、柱≤DEA与样本期硬闸。
    windows = monthly[monthly['window']].copy()

    candidates = []
    holding = False
    entry_date = None
    exit_date = None
    window_blocked_until = None

    for _, window in windows.iterrows():
        window_start = window['month_start']
        window_end = window['month_end']
        if window_end < BACKTEST_START or window_start > BACKTEST_END:
            continue

        year = window_start.year if window_start.month >= 4 else window_start.year - 1
        if year not in eligibility or not eligibility[year][0]:
            continue

        # 一个窗口存活期间，后续柱体波动不重复开窗。
        if window_blocked_until is not None and window_start <= window_blocked_until:
            continue

        # 即使已预先模拟出未来退出日，也不能在真实持仓区间内生成重叠候选。
        if exit_date is not None and window_start <= exit_date:
            continue
        if exit_date is not None and window_start > exit_date:
            holding = False

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
        if not entry or entry.get('status') != 'entered':
            window_blocked_until = entry.get('window_end_date', valid_until) if entry else valid_until
            continue

        entry_date = entry['entry_date']
        entry_price = entry['entry_price']
        window_blocked_until = entry_date
        if entry_date > BACKTEST_END:
            continue

        exit_result = simulate_exit(
            weekly,
            entry_price,
            entry_date,
            end_date=BACKTEST_END,
            daily=daily,
            exit_mode=EXIT_MODE,
        )
        exit_date = exit_result.get('exit_date', exit_result.get('last_date'))

        candidate = {
            'code': code,
            'name': name,
            'window_month': window_end.strftime('%Y-%m'),
            'entry_date': entry_date,
            'entry_price': entry_price,
            'green_bar_date': entry['green_bar_date'],
            'reference_price': entry['reference_price'],
            'selection_score': eligibility[year][1],
            'entry_year': year,
            **exit_result,
        }
        candidates.append(candidate)
        holding = exit_result['status'] == 'holding'

    return candidates


def simulate_portfolio(candidates: List[Dict]) -> Tuple[List[Dict], pd.DataFrame]:
    """
    事件驱动组合模拟：10万本金，每只股票1万，最多10只，按选股评分择优录取。
    返回实际执行的交易列表和每日账户日志。
    """
    if not candidates:
        return [], pd.DataFrame()

    cand_df = pd.DataFrame(candidates)
    if 'exit_date' not in cand_df.columns:
        cand_df['exit_date'] = pd.NaT
    if 'last_date' not in cand_df.columns:
        cand_df['last_date'] = pd.NaT
    cand_df['entry_date'] = pd.to_datetime(cand_df['entry_date'])
    cand_df['exit_date'] = pd.to_datetime(cand_df['exit_date'], errors='coerce')
    cand_df['last_date'] = pd.to_datetime(cand_df['last_date'], errors='coerce')
    cand_df['return_pct'] = pd.to_numeric(cand_df['return_pct'], errors='coerce')

    # 按入场日期、评分排序；同一天评分高的优先。同股同日若由重叠窗口
    # 产生多个候选，只保留更早的有效窗口，严格落实单股单仓位。
    cand_df = cand_df.sort_values(
        ['entry_date', 'selection_score', 'window_month'],
        ascending=[True, False, True],
    ).drop_duplicates(['entry_date', 'code'], keep='first').reset_index(drop=True)

    cash = INITIAL_CAPITAL
    positions: List[Dict] = []
    executed: List[Dict] = []
    daily_log: List[Dict] = []

    # 所有事件日期：候选入场日、独立退出日、回测截止日。
    # 退出日必须单独进入事件轴，否则只有出现下一笔入场时旧仓才会释放现金。
    event_dates = set(cand_df['entry_date'].dropna().tolist())
    event_dates.update(cand_df['exit_date'].dropna().tolist())
    event_dates.add(BACKTEST_END)
    event_dates = sorted(event_dates)

    for event_date in event_dates:
        if event_date > BACKTEST_END:
            continue

        # 1. 处理当日到期的持仓，释放现金
        matured = [p for p in positions if pd.notna(p['exit_date']) and p['exit_date'] <= event_date]
        for p in matured:
            proceeds = POSITION_SIZE * (1 + p['return_pct'] / 100)
            cash += proceeds
            executed.append({**p, 'actual_exit_date': p['exit_date']})
        positions = [
            p for p in positions
            if pd.isna(p['exit_date']) or p['exit_date'] > event_date
        ]

        # 处理持有中（到end_date仍无exit_date）：按当前return_pct估值，但暂不释放
        # 这里持有中只是未实现，不影响现金

        # 2. 获取当日新触发的候选信号
        day_candidates = cand_df[cand_df['entry_date'] == event_date].copy()
        # 去掉已经在持仓中的股票
        held_codes = {p['code'] for p in positions}
        day_candidates = day_candidates[~day_candidates['code'].isin(held_codes)]

        # 3. 按评分择优录取，直到资金或仓位用完
        slots = MAX_POSITIONS - len(positions)
        budget_slots = int(cash // POSITION_SIZE)
        available = min(slots, budget_slots)

        for _, row in day_candidates.iterrows():
            if available <= 0:
                break
            position = {
                'code': row['code'],
                'name': row['name'],
                'window_month': row['window_month'],
                'entry_date': row['entry_date'],
                'entry_price': row['entry_price'],
                'entry_score': row['selection_score'],
                'exit_date': row['exit_date'] if pd.notna(row['exit_date']) else None,
                'last_date': row.get('last_date'),
                'return_pct': row['return_pct'],
                'status': row['status'],
                'exit_reason': row.get('exit_reason', ''),
            }
            positions.append(position)
            cash -= POSITION_SIZE
            available -= 1

        # 4. 记录当日账户状态
        # 事件日之间没有逐日价格路径，历史事件点按成本记账；回测截止日才按
        # simulate_exit 返回的截止日收益对未平仓头寸做市值计量，避免未来收益泄漏。
        if event_date == BACKTEST_END:
            holding_value = POSITION_SIZE * sum(
                (1 + (p['return_pct'] / 100 if pd.notna(p['return_pct']) else 0.0))
                for p in positions
            )
        else:
            holding_value = POSITION_SIZE * len(positions)
        daily_log.append({
            'date': event_date,
            'cash': round(cash, 2),
            'positions': len(positions),
            'holding_value': round(holding_value, 2),
            'total_value': round(cash + holding_value, 2),
        })

    # 把仍在持仓的也加入 executed
    for p in positions:
        executed.append({**p, 'actual_exit_date': p.get('last_date')})

    return executed, pd.DataFrame(daily_log)


def process_chunk(args) -> str:
    chunk_idx, codes, names, market_regime, eligibility = args
    print(f'[Chunk {chunk_idx}] 开始处理 {len(codes)} 只股票...', flush=True)

    print(f'[Chunk {chunk_idx}] 加载行情...', flush=True)
    prices = load_prices(codes, START_DATE, END_DATE)

    print(f'[Chunk {chunk_idx}] 生成候选信号...', flush=True)
    all_candidates = []
    for code in codes:
        name = names[code]
        daily = prices[prices['S_INFO_WINDCODE'] == code].rename(columns={
            'TRADE_DT': 'date',
            'S_DQ_ADJOPEN': 'open',
            'S_DQ_ADJHIGH': 'high',
            'S_DQ_ADJLOW': 'low',
            'S_DQ_ADJCLOSE': 'close',
        })
        candidates = run_backtest_for_stock(code, name, daily, eligibility[code], market_regime)
        all_candidates.extend(candidates)

    output_path = DATA_DIR / f'candidate_trades_{RUN_TAG}_chunk_{chunk_idx}.csv'
    if all_candidates:
        df = pd.DataFrame(all_candidates)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    else:
        pd.DataFrame().to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f'[Chunk {chunk_idx}] 完成，候选信号数：{len(all_candidates)}，保存到 {output_path}', flush=True)
    return str(output_path)


def build_annual_summary(trades_df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
    trades = trades_df.copy()
    trades['entry_date'] = pd.to_datetime(trades['entry_date'])
    trades['actual_exit_date'] = pd.to_datetime(trades['actual_exit_date'], errors='coerce')
    trades['return_pct'] = pd.to_numeric(trades['return_pct'], errors='coerce')
    trades['entry_year'] = trades['entry_date'].dt.year

    records = []
    for year in range(2020, 2027):
        year_trades = trades[trades['entry_year'] == year]
        completed = year_trades[year_trades['status'] != 'holding']
        holding = year_trades[year_trades['status'] == 'holding']

        if len(completed) > 0:
            wins = completed[completed['return_pct'] > 0]
            win_rate = len(wins) / len(completed) * 100
            avg_ret = completed['return_pct'].mean()
            med_ret = completed['return_pct'].median()
        else:
            win_rate = avg_ret = med_ret = 0.0

        cohort_ret = year_trades['return_pct'].mean() if len(year_trades) > 0 else 0.0

        records.append({
            'year': year,
            'new_trades': len(year_trades),
            'completed': len(completed),
            'holding': len(holding),
            'win_rate_pct': round(win_rate, 2),
            'avg_return_pct': round(avg_ret, 2),
            'median_return_pct': round(med_ret, 2),
            'entry_cohort_avg_return_pct': round(cohort_ret, 2),
        })

    annual = pd.DataFrame(records)
    cumulative = (1 + annual['entry_cohort_avg_return_pct'] / 100).prod()
    return annual, cumulative


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(
        f'参数：ROE阈值={ROE_THRESHOLD}%，金字塔行业内前10%，'
        f'10万资金/1万每仓/最多10仓，退出模式={EXIT_MODE}，'
        f'截止={BACKTEST_END.date()}',
        flush=True,
    )

    universe = load_stock_universe()
    codes = universe['code'].tolist()
    names = dict(zip(universe['code'], universe['name']))
    print(f'股票池数量：{len(codes)}', flush=True)

    # 加载财务数据 + 行业归属（全局计算选股评分与金字塔过滤）
    print('加载财务数据...', flush=True)
    fi, bs = load_financial_data(codes)
    print('加载行业归属...', flush=True)
    industry_membership = load_industry_membership()
    years = list(range(2020, 2027))

    print('计算选股评分 + 金字塔行业前10%过滤...', flush=True)
    eligibility = build_eligibility_and_scores(fi, bs, codes, years, industry_membership)
    n_eligible = {y: sum(1 for c in codes if eligibility[c][y][0]) for y in years}
    print(f'每年合格股票数：{n_eligible}', flush=True)

    # 分块处理（行情加载与信号生成并行）
    n_chunks = 8
    chunk_size = (len(codes) + n_chunks - 1) // n_chunks
    chunks = []
    for i in range(n_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, len(codes))
        chunk_codes = codes[start:end]
        chunks.append((i, chunk_codes, names, None, eligibility))

    print(f'分成 {n_chunks} 个子集并行处理...', flush=True)
    with mp.Pool(processes=n_chunks) as pool:
        chunk_files = pool.map(process_chunk, chunks)

    print('汇总所有候选信号...', flush=True)
    all_candidates = []
    for f in chunk_files:
        df = pd.read_csv(f)
        if not df.empty:
            all_candidates.append(df)

    if not all_candidates:
        print('未产生任何候选信号。', flush=True)
        return

    candidates_df = pd.concat(all_candidates, ignore_index=True)
    candidates_df.to_csv(DATA_DIR / f'candidate_trades_{RUN_TAG}.csv', index=False, encoding='utf-8-sig')
    print(f'候选信号总数：{len(candidates_df)}，已保存', flush=True)

    # 组合模拟
    print('执行组合资金模拟...', flush=True)
    executed_trades, portfolio_log = simulate_portfolio(candidates_df.to_dict('records'))
    if not executed_trades:
        print('组合未执行任何交易。', flush=True)
        return

    trades_df = pd.DataFrame(executed_trades)
    trades_df.to_csv(DATA_DIR / f'large_scale_trades_portfolio_{RUN_TAG}.csv', index=False, encoding='utf-8-sig')
    portfolio_log.to_csv(DATA_DIR / f'portfolio_log_{RUN_TAG}.csv', index=False, encoding='utf-8-sig')
    print(f'实际执行交易数：{len(trades_df)}', flush=True)

    # 整体统计
    completed = trades_df[trades_df['status'] != 'holding'].copy()
    holding_df = trades_df[trades_df['status'] == 'holding']
    unique_stocks = trades_df['code'].nunique()
    wins = completed[completed['return_pct'] > 0]
    losses = completed[completed['return_pct'] <= 0]

    summary = {
        'backtest_start': BACKTEST_START.strftime('%Y-%m-%d'),
        'backtest_end': BACKTEST_END.strftime('%Y-%m-%d'),
        'initial_capital': INITIAL_CAPITAL,
        'position_size': POSITION_SIZE,
        'max_positions': MAX_POSITIONS,
        'exit_mode': EXIT_MODE,
        'total_trades': int(len(trades_df)),
        'completed_trades': int(len(completed)),
        'holding_trades': int(len(holding_df)),
        'unique_stocks': int(unique_stocks),
        'win_rate_pct': round(len(wins) / len(completed) * 100, 2) if len(completed) > 0 else 0.0,
        'avg_return_pct': round(completed['return_pct'].mean(), 2) if len(completed) > 0 else 0.0,
        'median_return_pct': round(completed['return_pct'].median(), 2) if len(completed) > 0 else 0.0,
        'max_single_gain_pct': round(completed['return_pct'].max(), 2) if len(completed) > 0 else 0.0,
        'max_single_loss_pct': round(completed['return_pct'].min(), 2) if len(completed) > 0 else 0.0,
        'fixed_stop_exits': int((completed['exit_reason'] == 'fixed_cost_stop').sum()),
        'website_tiered_stop_exits': int((completed['exit_reason'] == 'website_tiered_stop').sum()),
        'weekly_low_exits': int((completed['exit_reason'] == 'weekly_low').sum()),
        'realized_pnl': round((POSITION_SIZE * completed['return_pct'] / 100).sum(), 2),
        'unrealized_pnl': round((POSITION_SIZE * holding_df['return_pct'] / 100).sum(), 2),
    }

    annual, cumulative_nav = build_annual_summary(trades_df)
    summary['entry_cohort_compounded_nav'] = round(cumulative_nav, 4)

    # 组合最终净值（按每日账户价值）
    if not portfolio_log.empty:
        final_value = portfolio_log['total_value'].iloc[-1]
        summary['portfolio_final_value'] = round(final_value, 2)
        summary['portfolio_total_return_pct'] = round((final_value / INITIAL_CAPITAL - 1) * 100, 2)

    annual.to_csv(DATA_DIR / f'annual_summary_portfolio_{RUN_TAG}.csv', index=False, encoding='utf-8-sig')

    print('\n========== 整体回测统计（固定-40%止损·周最低价单条件止盈） ==========', flush=True)
    for k, v in summary.items():
        print(f'{k}: {v}', flush=True)

    print('\n========== 年度汇总（按入场年份分组） ==========', flush=True)
    print(annual.to_string(index=False), flush=True)
    print(f'\n入场年份分组平均收益连乘（非真实账户净值）: {cumulative_nav:.4f}', flush=True)
    if not portfolio_log.empty:
        print(f'2020-2026 组合账户最终价值: {portfolio_log["total_value"].iloc[-1]:.2f}', flush=True)

    with open(DATA_DIR / f'large_scale_summary_portfolio_{RUN_TAG}.json', 'w', encoding='utf-8') as f:
        json.dump({**summary, 'annual': annual.to_dict(orient='records')}, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)
    main()
