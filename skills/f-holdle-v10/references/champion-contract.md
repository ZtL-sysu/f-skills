# HOLDLE v10 综合冠军冻结契约

## 1. 身份与来源

- 冠军标签：`composite_champion`
- 选股：`sel-1ec754339a53a397`
- 买入：`ent-6fa74d3c9181a9b9`
- 原组合：`port-ed1797c5a175944a`（7/2/2，仅保留为历史来源）
- 当前组合：`port-5b717f19eed2a045`（10/2/2，容量覆盖后默认）
- 权威来源：
  - `${HOLDLE_V10_RESULTS_ROOT:-${HOLDLE_OUTPUT_ROOT:-${HOLDLE_ROOT:-$HOME/code/holdle}/04_训练记录}/v10_2020_2026_full_rank}/results/champions/composite_champion/summary.json`
  - `${HOLDLE_V10_RESULTS_ROOT:-${HOLDLE_OUTPUT_ROOT:-${HOLDLE_ROOT:-$HOME/code/holdle}/04_训练记录}/v10_2020_2026_full_rank}/reports/v10_2020_2026_champions.json`
  - `${HOLDLE_V10_RESULTS_ROOT:-${HOLDLE_OUTPUT_ROOT:-${HOLDLE_ROOT:-$HOME/code/holdle}/04_训练记录}/v10_2020_2026_full_rank}/candidates/*.jsonl`

## 2. 冻结参数

### 选股

- 近5年最低ROE≥6%
- 近5年平均ROE≥12%
- ROE线性斜率≥0个百分点/年
- 近5年最高资产负债率≤60%
- 申万三级行业内前20%
- 权重：ROE/净利率/毛利率/现金占比/负债稳定/EPS = 40/15/15/15/10/5

### 买入

- 月MACD柱≥0.3
- 至少30根完整月K
- 日K绿柱确认后最多等待40个交易日突破
- 保留状态A、柱≤DEA、盘中最高价严格突破参考价等 v10 原规则

### 组合与成本

- 初始资金100,000元；每仓10,000元；最多10仓
- 申万一级最多2仓；申万三级最多2仓
- 佣金0.03%，最低5元；单边滑点5bp；卖出印花税0.1%

### 卖出

- 固定止损：成本×0.60，日内最低价触线执行
- 盈利保护：官网周K有效低点；周最低价与完整周收盘价双确认

形式化实现与回归基线：

- `$CODEX_HOME/skills/f-holdle/scripts/unified_backtest_v2.py`
- `$CODEX_HOME/skills/f-holdle/scripts/weekly_low_exit.py`
- `${HOLDLE_ROOT:-$HOME/code/holdle}/gj/article_3_wuxi.txt`
- `${HOLDLE_ROOT:-$HOME/code/holdle}/gj/article_4_midea.txt`
- `${HOLDLE_ROOT:-$HOME/code/holdle}/gj/article_5_dongpeng.txt`

## 3. 数据与目录

- 默认金融数据源：`$gjdata`，核心行情表 `AShareEODPrices`
- 价格字段：Wind后复权OHLC；成交与实盘报价必须另行标注原始价格
- 当前本地 v10 可研究交易时间轴：2010-01-01至本地最新完整交易日；价格预热可早于2010
- 研究/回测：`${HOLDLE_OUTPUT_ROOT:-${HOLDLE_ROOT:-$HOME/code/holdle}/04_训练记录}/`
- 实盘咨询：`${HOLDLE_LIVE_ROOT:-${HOLDLE_ROOT:-$HOME/code/holdle}/05_上岗指令}/`

## 4. 滚动窗口协议

- 每个窗口独立从100,000元起跑，窗口前持仓不继承。
- 默认生成每年起步的完整日历窗口：`[Y-01-01, (Y+N-1)-12-31]`，N∈{3,5,6,7}。
- 另加一个精确截至最新完整交易日的尾部窗口，标为 `trailing_to_latest`，不得与完整日历窗口混为同一类排名。
- 复跑候选集默认是原综合前50与原净值前20的并集；先保留67个源三元组，再在容量覆盖后记录有效配置去重映射。
- 只把总仓位上限改成10；保留每个源组合的申万一级/三级上限。冠军默认固定10/2/2。
- 所有窗口必须独立重放单股阻塞、组合容量、成本和截至窗口末日的持仓估值。

## 5. 必须报告的风险

- 候选来自2020–2026研究排名，早期与后期滚动窗口都是回看稳健性分析，不构成真正未触碰盲测。
- 同一策略在高度重叠窗口中的结果不独立。
- 报告头部3笔依赖、剔除头部3笔损益、已实现/未实现损益和资金利用率。
- 不将回撤作为止损；唯一亏损强制线仍为固定成本-40%。
