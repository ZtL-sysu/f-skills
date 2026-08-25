"""
HOLDLE 选股规则实现

规则来源：01_原始资料/04_第2章_选股篇.md

核心指标（按重要性排序）：
1. ROE：5年平稳或逐年上升，>=10%合格，>=20%稳健，>=35%优秀
2. 毛利率：>=20%稳健，>=30%优秀，稳定优先
3. 净利率：>=10%合格，>=20%优秀，稳定优先
4. 现金占总资产比率：5年均值>=10%合格，>=25%安全
5. 负债率：稳定，不要逐年飙升
6. 总资产周转率：同行业对比
7. EPS：持续增长

金字塔逻辑：同行业排名前10%（本模块先实现单只股票基本面评分，行业排名需要批量）
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np


CODEX_HOME = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')).expanduser()
GJDATA_SCRIPTS = CODEX_HOME / 'skills/gjdata/scripts'


def gjdata_get(table: str, code: str, period: Optional[str] = None,
               start: Optional[str] = None, end: Optional[str] = None,
               cols: Optional[List[str]] = None, where: Optional[str] = None,
               limit: int = 5000) -> pd.DataFrame:
    """调用 gjdata stock.py get 取数，返回 DataFrame。"""
    script = GJDATA_SCRIPTS / 'stock.py'
    cmd = ['python', str(script), 'get', '--table', table, '--code', code,
           '--limit', str(limit), '--format', 'json']
    if period:
        cmd += ['--period', period]
    if start:
        cmd += ['--start', start]
    if end:
        cmd += ['--end', end]
    if cols:
        cmd += ['--cols', ','.join(cols)]
    if where:
        cmd += ['--where', where]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    rows = json.loads(result.stdout)
    return pd.DataFrame(rows)


def fetch_financial_indicator(code: str, end_period: Optional[str] = None,
                              n_years: int = 5) -> pd.DataFrame:
    """获取 AShareFinancialIndicator 年度数据（合并报表）。"""
    cols = ['S_INFO_WINDCODE', 'REPORT_PERIOD', 'STATEMENT_TYPE',
            'S_FA_ROE', 'S_FA_GROSSPROFITMARGIN', 'S_FA_NETPROFITMARGIN',
            'S_FA_ASSETSTURN', 'S_FA_EPS_BASIC', 'S_FA_DEBTTOASSETS']
    where = "STATEMENT_TYPE='合并报表'"
    if end_period:
        where += f" AND REPORT_PERIOD<='{end_period}'"
    df = gjdata_get('AShareFinancialIndicator', code, cols=cols, where=where)
    if df.empty:
        return df
    df['REPORT_PERIOD'] = pd.to_datetime(df['REPORT_PERIOD'], format='%Y%m%d')
    # 只保留年报（12-31）
    df = df[df['REPORT_PERIOD'].dt.month == 12].copy()
    for c in ['S_FA_ROE', 'S_FA_GROSSPROFITMARGIN', 'S_FA_NETPROFITMARGIN',
              'S_FA_ASSETSTURN', 'S_FA_EPS_BASIC', 'S_FA_DEBTTOASSETS']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.sort_values('REPORT_PERIOD').tail(n_years).reset_index(drop=True)
    return df


def fetch_balance_sheet(code: str, end_period: Optional[str] = None,
                        n_years: int = 5) -> pd.DataFrame:
    """获取 AShareBalanceSheet 年度数据，取合并报表（408001000）。"""
    cols = ['S_INFO_WINDCODE', 'REPORT_PERIOD', 'STATEMENT_TYPE',
            'MONETARY_CAP', 'TOT_ASSETS', 'TOT_LIAB']
    where = "STATEMENT_TYPE='408001000'"
    if end_period:
        where += f" AND REPORT_PERIOD<='{end_period}'"
    df = gjdata_get('AShareBalanceSheet', code, cols=cols, where=where)
    if df.empty:
        return df
    df['REPORT_PERIOD'] = pd.to_datetime(df['REPORT_PERIOD'], format='%Y%m%d')
    df = df[df['REPORT_PERIOD'].dt.month == 12].copy()
    for c in ['MONETARY_CAP', 'TOT_ASSETS', 'TOT_LIAB']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.sort_values('REPORT_PERIOD').tail(n_years).reset_index(drop=True)
    return df


def trend_score(values: pd.Series, stable_cv: float = 0.15) -> Dict:
    """
    评估序列趋势：平稳/上升/下降/波动。
    对百分比指标使用相对阈值：斜率相对均值 < 5%/年 视为平稳。
    """
    values = values.dropna()
    if len(values) < 2:
        return {'trend': 'unknown', 'slope': np.nan, 'cv': np.nan, 'stability': 'unknown'}
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    mean_v = values.mean()
    std_v = values.std()
    cv = std_v / abs(mean_v) if mean_v != 0 else np.nan
    # 相对斜率：年均变化 / 均值
    rel_slope = slope / abs(mean_v) if mean_v != 0 else np.nan
    if rel_slope > 0.05:
        trend = 'rising'
    elif rel_slope < -0.05:
        trend = 'falling'
    else:
        trend = 'stable'
    stability = 'stable' if cv < stable_cv else ('moderate' if cv < 0.30 else 'volatile')
    return {'trend': trend, 'slope': slope, 'cv': cv, 'rel_slope': rel_slope, 'stability': stability}


def evaluate_stock(code: str, name: str, reference_date: Optional[str] = None,
                   n_years: int = 5, mode: str = 'practical') -> Dict:
    """
    对单只股票执行 HOLDLE 选股规则评估。

    reference_date: 参考日期，如 '20240501'。评估使用该日期前最近N年年报。
                    若为空，则使用最新年报。
    mode: 'course'  严格按课程文字（ROE>=10%、净利率>=10% 等）
          'practical' 网站实战口径（ROE>=20% 或 18-22%边界综合判断；
                        净利率>=9%且趋势向上可接受；默认）
    """
    end_period = reference_date if reference_date else None

    fi = fetch_financial_indicator(code, end_period, n_years)
    bs = fetch_balance_sheet(code, end_period, n_years)

    result = {
        'code': code,
        'name': name,
        'reference_date': reference_date,
        'n_years': n_years,
        'mode': mode,
        'data_years': len(fi),
        'checks': {},
        'passed': False,
        'score': 0,
        'details': {},
    }

    if fi.empty or bs.empty:
        result['checks']['data_available'] = {'passed': False, 'reason': '财务数据不足，无法评估'}
        result['summary'] = '财务数据不足，无法评估'
        return result

    # ---- ROE ----
    roe = fi['S_FA_ROE']
    roe_trend = trend_score(roe, stable_cv=0.20)
    roe_latest = roe.iloc[-1]
    if mode == 'course':
        # 课程文字：>=10%合格，>=20%稳健，>=35%优秀；5年基本平稳
        roe_pass = roe_latest >= 10 and roe_trend['stability'] != 'volatile'
        roe_req = '最新>=10%，5年基本平稳（CV<20%）'
    else:
        # 网站实战：ROE>=20% 直接通过；18-22% 边界区需其他指标辅助通过
        roe_pass = roe_latest >= 20 or (roe_latest >= 18 and roe_trend['stability'] != 'volatile')
        roe_req = '最新>=20%（或18-22%边界区且稳定）'
    result['checks']['roe'] = {
        'passed': roe_pass,
        'latest': round(roe_latest, 2),
        'trend': roe_trend['trend'],
        'stability': roe_trend['stability'],
        'values': [round(v, 2) for v in roe.tolist()],
        'requirement': roe_req,
    }

    # ---- 毛利率 ----
    gm = fi['S_FA_GROSSPROFITMARGIN']
    gm_trend = trend_score(gm)
    gm_latest = gm.iloc[-1]
    gm_pass = gm_latest >= 20 and gm_trend['stability'] != 'volatile'
    result['checks']['gross_margin'] = {
        'passed': gm_pass,
        'latest': round(gm_latest, 2),
        'trend': gm_trend['trend'],
        'stability': gm_trend['stability'],
        'values': [round(v, 2) for v in gm.tolist()],
        'requirement': '最新>=20%，趋势稳定',
    }

    # ---- 净利率 ----
    nm = fi['S_FA_NETPROFITMARGIN']
    nm_trend = trend_score(nm)
    nm_latest = nm.iloc[-1]
    if mode == 'course':
        nm_pass = nm_latest >= 10 and nm_trend['stability'] != 'volatile'
        nm_req = '最新>=10%，趋势稳定'
    else:
        # 网站实战：>=10% 理想；9-10% 边界且趋势向上/稳定可接受；
        # 若 ROE>=20% 且净利率>=20%，高波动也可包容
        nm_pass = (
            nm_latest >= 10
            or (nm_latest >= 9 and nm_trend['trend'] in ('rising', 'stable'))
            or (roe_latest >= 20 and nm_latest >= 20)
        )
        nm_req = '最新>=10%（或>=9%且趋势向上；或ROE>=20%且净利率>=20%）'
    result['checks']['net_margin'] = {
        'passed': nm_pass,
        'latest': round(nm_latest, 2),
        'trend': nm_trend['trend'],
        'stability': nm_trend['stability'],
        'values': [round(v, 2) for v in nm.tolist()],
        'requirement': nm_req,
    }

    # ---- 现金占总资产比率 ----
    bs = bs.sort_values('REPORT_PERIOD').reset_index(drop=True)
    bs['cash_ratio'] = bs['MONETARY_CAP'] / bs['TOT_ASSETS'] * 100
    cash_avg = bs['cash_ratio'].mean()
    cash_pass = cash_avg >= 10
    result['checks']['cash_to_assets'] = {
        'passed': cash_pass,
        '5y_avg': round(cash_avg, 2),
        'values': [round(v, 2) for v in bs['cash_ratio'].tolist()],
        'requirement': '5年均值>=10%',
    }

    # ---- 负债率 ----
    debt = fi['S_FA_DEBTTOASSETS']
    debt_trend = trend_score(debt)
    debt_latest = debt.iloc[-1]
    # 允许高但稳定；飙升才危险
    debt_pass = not (debt_trend['trend'] == 'rising' and debt_trend['cv'] > 0.15)
    result['checks']['debt_ratio'] = {
        'passed': debt_pass,
        'latest': round(debt_latest, 2),
        'trend': debt_trend['trend'],
        'stability': debt_trend['stability'],
        'values': [round(v, 2) for v in debt.tolist()],
        'requirement': '负债率稳定，不飙升',
    }

    # ---- 总资产周转率 ----
    at = fi['S_FA_ASSETSTURN']
    result['checks']['asset_turnover'] = {
        'passed': None,  # 需同行业对比，单股无法判定
        'latest': round(at.iloc[-1], 3) if not at.empty else None,
        'values': [round(v, 3) for v in at.tolist()],
        'requirement': '同行业对比（本模块单股不做判定）',
    }

    # ---- EPS ----
    eps = fi['S_FA_EPS_BASIC'].dropna()
    # 忽略最早的 0 值（数据异常或拆分前），从第一个非零值开始算整体增长
    eps_nonzero = eps[eps != 0]
    if len(eps_nonzero) >= 2:
        eps_growth = (eps_nonzero.iloc[-1] - eps_nonzero.iloc[0]) / abs(eps_nonzero.iloc[0]) * 100
    else:
        eps_growth = None
    # 同时检查是否逐年增长（允许小幅波动 < 10%）
    yoy_growths = eps_nonzero.pct_change().dropna() if len(eps_nonzero) >= 2 else pd.Series(dtype=float)
    eps_pass = (
        eps_growth is not None and eps_growth >= 0
    ) or (
        len(yoy_growths) >= 1 and yoy_growths.mean() >= 0 and (yoy_growths < -0.10).sum() <= 1
    )
    result['checks']['eps'] = {
        'passed': eps_pass,
        'growth_pct': round(eps_growth, 2) if eps_growth is not None else None,
        'yoy_values': [round(v, 3) for v in yoy_growths.tolist()],
        'values': [round(v, 3) for v in eps.tolist()],
        'requirement': '5年持续增长（允许一次>10%下滑）',
    }

    # ---- 综合评分 ----
    checks = result['checks']
    score = 0
    weights = {
        'roe': 0.30,
        'gross_margin': 0.20,
        'net_margin': 0.15,
        'cash_to_assets': 0.15,
        'debt_ratio': 0.10,
        'eps': 0.10,
    }
    for key, w in weights.items():
        if checks[key]['passed']:
            score += w * 100

    result['score'] = round(score, 1)

    # 必须项：ROE、毛利率、净利率、现金、EPS 都通过才算基本面合格
    must_pass = ['roe', 'gross_margin', 'net_margin', 'cash_to_assets', 'eps']
    result['passed'] = all(checks[k]['passed'] for k in must_pass)

    # 数据年限警告
    if len(fi) < n_years:
        result['warnings'] = [f"实际可用年报仅{len(fi)}年，少于要求的{n_years}年"]
    else:
        result['warnings'] = []

    return result


def print_report(result: Dict):
    """打印选股评估报告。"""
    print(f"\n{'='*60}")
    print(f"选股评估报告：{result['name']} ({result['code']})")
    print(f"参考日期：{result['reference_date']} | 模式：{result['mode']} | 5年要求/实际：{result['n_years']}/{result['data_years']}")
    print(f"{'='*60}")

    for key, check in result['checks'].items():
        status = '✅' if check.get('passed') else ('⏸️' if check.get('passed') is None else '❌')
        print(f"\n{status} {key}")
        print(f"   最新值/5年均：{check.get('latest')} / {check.get('5y_avg')}")
        print(f"   趋势：{check.get('trend')} | 稳定性：{check.get('stability')}")
        print(f"   历史值：{check.get('values')}")
        print(f"   标准：{check.get('requirement')}")

    print(f"\n综合评分：{result['score']}/100")
    print(f"是否通过：{'✅ 通过' if result['passed'] else '❌ 未通过'}")
    if result['warnings']:
        print(f"警告：{'; '.join(result['warnings'])}")


if __name__ == '__main__':
    # 东鹏饮料 2024-05 窗口前
    r = evaluate_stock('605499.SH', '东鹏饮料', reference_date='20240501')
    print_report(r)
