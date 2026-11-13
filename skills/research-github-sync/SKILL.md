---
name: research-github-sync
description: Coordinate research agents through a GitHub repository, standardized evidence checkpoints, incremental uploads, and resumable handoffs. Use when the user wants agents to work together or continue each other's research while syncing progress to GitHub.
---

# Research GitHub Sync

让其他 agent 只读仓库就能按同一协议协作或接续；工作中持续上传小而完整的检查点。适用于 Codex、WorkBuddy 和其他能读 Markdown、使用 Git 的 agent，不依赖特定模型或会话工具。

## 启动与授权

1. 确认用户指定的仓库、任务和可写范围。先读仓库 AGENTS.md、`collaboration/PROTOCOL.md`、`collaboration/PROJECT.md`、相应 TASK 和各 agent 的最新 HANDOFF；再核实实际源码、结果与作业状态。旧日志不能自动证明当前进程仍活着或已停止。
2. 用户给任务时明确带上本 skill，且已指定或当前上下文唯一确定目标仓库，即授权将该任务的必要代码、结果、日志及交接记录持续提交到该仓库的 agent 分支，无需每次 push 再确认。仅创建/安装 skill 不授权发布其他研究材料。没有可确定的仓库，先做本地工作并询问仓库地址；不要猜账号或创建公开仓库。
3. 新项目缺少协作文件时，依据 [统一格式](references/FORMAT.md) 与 assets 模板补齐。协议只约束记录与同步，不能替换用户科研目标、实验范围、验收指标或原项目科学流程。已有历史产物保持原路径，用索引引用，不为统一格式搬移或改写证据。

## 并行与续接

- 每个工作者用独立 clone/worktree、唯一 agent_id 和 `agent/<task_id>/<agent_id>` 分支；先 fetch 最新主线和相关 agent 分支，不在共享脏工作区 checkout/reset/stash。续接时读取前任分支和提交，另建自己的分支，保留前任记录。
- TASK.md 指定任务 owner、依赖、可写路径与停止条件；只有 owner 更新 TASK。各 agent 只写自己的 HANDOFF、LOG、检查点和分配到的代码/结果路径。发现同一文件或同一实验已被认领，先按现有分工协调；不要重复启动作业或覆盖他人结果。
- 独立分支不是任务锁。读已公布的其他 agent 交接；遇到重叠的活动任务且无可靠状态可核实，暂停重叠部分，继续可独立完成的工作。不得编造“已协商”。
- 工作分支 push 是共享进度，合入默认分支是验收结果。默认分支仅由任务明确指定的整合者验收后合并。skill 不自动授权 merge、force push、删除远程分支、发布 Release 或向他人发消息。

## 边干边传

首次认领/接续、重要代码或实验结论形成、长实验启动/结束、遇到失败/阻塞、交接前都提交检查点。持续工作时通常每 15–30 分钟整理一次有意义的变化，不逐工具调用提交。长作业记录 provider、真实 job_id、最近核实时间和恢复命令；只上传轻量状态，不每次打包权重。

每次同步按 [统一格式](references/FORMAT.md)：

1. 更新自己的 HANDOFF；LOG 只追加本轮关键决策、失败与原因。成功结果保留复现所需代码、配置、原始指标及必要证据；失败默认只传摘要和必要小反例，完整失败大产物留本地。
2. 使用 assets 的 CHECKPOINT.md 记录本轮事实、检查、局限、下一步；实验数字使用 METRICS.csv 的固定列。没有指标就不造空结果表，未完成不能写成成功。
3. 用 `scripts/checkpoint_manifest.py` 对实际 protocol/产物生成 SHA-256 清单，输出到本次检查点目录；清单描述提交前的输入 HEAD，不把“旧 HEAD”当作本次发布提交。新 commit SHA 由 Git 历史/链接定位，避免自引用哈希循环。
4. 检查 git diff 和明确文件清单，去除凭证、原始私人对话、本机身份路径、无关文件、数据缓存和重复大包。公开仓库的上传范围必须经过内容检查；未知权属/隐私材料只留本地，并在交接说明缺口。默认单文件超过 50 MiB 不上传，记录相对路径/哈希/大小及需安排的存储方式，不悄悄用 LFS/Release 绕过。
5. 只 stage 本轮明确产物，**不用 `git add .` / `git add -A`**。检查 staged diff，并确认目标 remote 属于用户指定仓库、当前分支是自己的任务分支；remote 身份记录不包含凭证。commit 后 push 自己的分支，然后核对远程分支 SHA 与本地 HEAD。报告“已上传”必须有远端确认；仅本地 commit 写“未同步”。

示例（先替换 task/agent/path，Git 参数逐项传递，不拼接不可信 shell 文本）：

```text
python -X utf8 <skill>/scripts/checkpoint_manifest.py create --repo . --task <task> --agent <agent> --status in_progress --protocol collaboration/tasks/<task>/TASK.md --artifact <code.py> --artifact <result.json> --out collaboration/tasks/<task>/agents/<agent>/checkpoints/<UTC-id>/manifest.json
python -X utf8 <skill>/scripts/checkpoint_manifest.py verify --repo . --manifest <manifest.json>
git add -- <explicit-file-1> <explicit-file-2> <checkpoint-directory>
git diff --cached --check
git diff --cached --stat
git commit -m "checkpoint(<task>/<agent>): <concrete outcome>"
git push -u origin HEAD:refs/heads/agent/<task>/<agent>
git ls-remote origin refs/heads/agent/<task>/<agent>
```

Windows 本机 Python 使用项目 Conda 环境；本 skill 不创建/切换全局环境或改 Git 全局配置。

维护此 skill 时可运行 `python -X utf8 <skill>/tests/test_checkpoint_manifest.py`。测试只使用临时 Git fixture，检查哈希、篡改、越界、重复覆盖和不自动提交等行为，不代表科研或远程上传验收。

## 冲突、离线与交接

- push 被拒：保留本地提交，fetch 后查清分支/owner。只在自己的干净分支上处理明确冲突；不 force push、不覆盖远程，也不无限重试。网络失败最多一次即时重试，仍失败记录未同步提交 SHA 和恢复命令，继续本地授权工作；交接/结束再试一次。
- 每次同步前复核当前协议版本。目标、split、baseline、选点、科学阈值发生实质改变，应按项目规则版本化并登记影响；旧结果保留，不能改哈希或改阈值把失败变成通过。
- HANDOFF 必须让新 agent 知道：读哪个协议/分支、哪些文件可靠、哪些结果仍待验收、有什么真实运行中的作业、下一条可执行命令及停止条件。缺失权重或远程数据明确写缺口。
- 最终回复简要给出仓库/分支或提交链接、完成与未完成事项、下个 agent 的入口。上传完成不等于科学结论成立或任务完成。禁止仅因代码/清单校验通过而宣称实验/论文验收通过。
