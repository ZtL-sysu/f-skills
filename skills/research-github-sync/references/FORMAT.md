# 统一上传格式 v1

本格式是协作记录层。项目原有代码、论文和实验目录不强制迁移；通过相对路径链接与 manifest 关联。

## 目录与单一写入者

```text
collaboration/
  PROTOCOL.md                  仓库协作规则，整合者维护
  PROJECT.md                   科研目标、协议入口、事实来源，整合者维护
  tasks/<task_id>/
    TASK.md                    本任务范围/验收/依赖/写入分工，task owner 维护
    agents/<agent_id>/
      HANDOFF.md               当前快照，仅该 agent 更新
      LOG.md                   追加式简明研究日志，仅该 agent 追加
      checkpoints/<UTC-id>/
        CHECKPOINT.md          一次事实记录，发布后不可回写
        manifest.json          本次协议/产物哈希，脚本生成
        metrics.csv            有真实测量时才存在
```

task_id/agent_id 使用小写字母、数字、短横线；agent_id 在仓库内唯一，建议日期+工具+随机后缀。UTC-id 用 `YYYYMMDDTHHMMSSZ-短后缀`。时间戳明确时区；科学结果中的百分数与小数不得混用。

## 必填记录

- **PROJECT**：用户目标；范围；当前科学协议/指导文件及版本；真实状态入口；历史材料定位；整合者及默认分支。未知事实写 unknown，不杜撰。
- **TASK**：task_id/owner；输入分支或提交；精确目标与验收；不在范围；依赖；分配给各 agent 的可写路径；执行/资源约束；协议变更方式。acceptance 必须可判定，不能只写“效果好”。
- **HANDOFF**：task/agent/branch；状态与最后更新时间；协议路径/哈希；已完成与未完成；当前可信产物链接；运行作业的实际核实状态；同步状态；自动合并结果（merged + commit / refused + 原因）；下一步命令及停止条件。成功声明必须指向对应结果。
- **LOG**：时间、尝试/变更、结果与局限、证据路径、决定/下一步。失败用这条简明记录，加必要反例；不上传整套重复失败权重与缓存。
- **CHECKPOINT**：本轮改动、实际执行命令、核验与结果、支持的结论、未支持的结论、产物路径、失败/风险、自动合并判定、下个动作。状态枚举 `in_progress / completed / blocked / failed` 是工作状态；`completed` 不自动代表科学主张成立。
- **manifest.json**：schema_version=1，task_id，agent_id，created_at_utc，status，input_git_head，protocol{path,sha256,bytes}，artifacts[{path,sha256,bytes}]。路径全部相对仓库。自己不包含自己的哈希；发布 commit 由 Git 定位。

## 实验表 metrics.csv

固定列：

```csv
task_id,agent_id,run_id,dataset,split,coverage,method,teacher_seed,student_seed,T,metric,value,unit,evidence,protocol_sha256,status
```

- 一行一个真实指标；`value` 是原始数值，`unit` 明确 `fraction / percent / pp / ms_per_graph / count` 等。
- `coverage` 写实际全量数量或明确 smoke/subset，不能只写 full；`split` 明确 train/val/test。
- 不适用字段留空；`status` 使用 `measured / failed / partial / historical`，目标值不混入实测表。
- `evidence` 指实际 JSON/NPZ/CSV/日志相对路径；`protocol_sha256` 必须对应执行协议。均值与样本 SD 使用独立 metric 名，保留每 seed 原值和 N。
- 统计/图表必须可回溯到表中原始证据；记录 checkpoint/source/data/calibration 身份、模型或运行配置的材料一起纳入 manifest。不要只传截图或只有最终均值。
- 结果失败、历史测试暴露、未忠实实现基线、成本分项未知等，明确保留在 CHECKPOINT/LOG，不能借统一模板掩盖。

## 发布包规则

优先小文件：关键代码/配置、真实指标、必要小预测/摘要、图表、复现命令、交接。需要大型权重/逐样本证据才能复现时，先复用仓库已存在且哈希核实的证据包，不每次复制；新增大包由项目约定存储，必须有 URL/相对路径、大小、SHA 与恢复办法。

每个 agent 的检查点不可覆盖。更正时发布新检查点，引用被更正记录与原因。滚动 HANDOFF 可更新，LOG 追加；旧 commit 与否定证据仍可追溯。共享 PROJECT/TASK 状态同样只在纯增量判定通过后自动合并；不能删改已有行来覆盖全局结论。

## 纯增量自动合并

`scripts/auto_merge.py` 比较「三方合并后的树」与「远端默认分支当前 HEAD」，只有同时满足以下条件才允许合并：

| 条件 | 要求 |
|---|---|
| 删除行数 | 0 |
| 已有行 | 不得改写或删除 |
| 文件状态 | 只允许 `A`（新增文件）与 `M`（已有文件仅追加行）；`D/R/C/T/U` 拒绝 |
| 二进制 | 只允许新增文件，已存在二进制不得变化 |
| 三方合并 | 无冲突 |
| 变更量 | 至少有一处新增 |

比较基准是**当前**默认分支，因此其他 agent 并发推进过也不影响：只要合入之后仍然只增不减就照合。满足时 `--execute` 执行 `merge --no-ff` + push，并用 `ls-remote` 确认远端 SHA；默认 dry run 只判定不改任何东西。不满足时输出带原因的 JSON 并拒绝合并且不 push。

记录要求：

- 每次同步把判定结果写入 CHECKPOINT 与 HANDOFF 的 `Auto-merge` 字段；`refused` 必须附脚本给出的原因。
- 更正一律用新检查点引用旧记录，不覆盖、不删除已有行，避免为了通过判定而改写历史证据。
- 自动合并是机械判定，不是科学验收；证据、指标与结论仍需按原项目流程核对。
- 禁止 force push、改写历史、删除远程分支；脚本与协议都不做这些操作。
