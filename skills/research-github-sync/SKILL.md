---
name: research-github-sync
description: Lightweight multi-agent project collaboration and research memory. Use when agents need to share project state, hand off work across sessions or tools, or sync progress and key findings through Git/GitHub.
---

# Research GitHub Sync

面向多 Agent 的轻量级项目协作与研究记忆协议。适用于 Codex、WorkBuddy，以及任何能读写项目文件、执行 Git 的 agent；覆盖科研实验、论文写作、软件开发、数据分析和长周期项目。

**唯一原则：文档是为了让下一个 agent 尽快接手，不是为了证明当前 agent 做过多少。**

## 何时使用

- 多个 agent 在同一项目轮流或并行工作，需要知道目标、进展与分工。
- 跨会话、跨工具接续任务，需要从前任记录恢复上下文。
- 需要通过 GitHub 同步进度，并保留重要结果、决策、失败经验与未完成事项。
- 不适合：一次性的普通 Git 操作、单人一次完成的任务、把本 skill 当通用 Git 工具。

## 首次进入项目：先发现，再复用

1. **只读最小集合**：项目入口（README.md / AGENTS.md / research_plan.md / docs/ 中实际存在的）、`collaboration/`（若有）、任务清单与最新 agent 记录。不要扫描全仓库历史日志。
2. **识别已有文档**：
   - 新版：`collaboration/STATE.md`、`collaboration/TASKS.md`、`collaboration/agents/<id>.md`。
   - 旧版：`collaboration/PROJECT.md`、`PROTOCOL.md`、`tasks/<task>/TASK.md`、`HANDOFF.md`、`CHECKPOINT.md`、`manifest.json`、`METRICS.csv`。
   旧文件一律**保留原路径**，读取信息后用相对链接引用；不重命名、不搬迁、不删除、不覆盖用户改过的文档，不删除旧实验记录。
3. **复用优先**：已有项目目标文档，STATE 只概括 + 链接，不复制全文；已有任务文件继续用，不强制迁移到 TASKS；已有研究记录不另建指标表。现有文档已足够协作时，可以不创建任何新文件。
4. **只补缺失**：需要时把 `assets/STATE.md`、`assets/TASKS.md` 复制到 `collaboration/`，把 `assets/AGENT.md` 复制为 `collaboration/agents/<agent_id>.md`。已存在的协作文件不覆盖，重复进入不重复生成。
5. 不改动 `src/`、`experiments/`、`paper/` 等原有目录，不为统一格式修改已有科研证据。

## 三种协作文档

| 文件 | 回答什么 | 谁写 | 何时写 |
|---|---|---|---|
| `collaboration/STATE.md` | 项目目标、整体进展、已验证结果、当前假设、已推翻结论、最大阻塞、下一步方向 | 任何 agent，项目级共识 | 项目级结论或方向变化时 |
| `collaboration/TASKS.md` | 有哪些任务、状态、负责人、范围、涉及文件/资源、依赖 | 认领任务的 agent | 认领、完成、阻塞时 |
| `collaboration/agents/<agent_id>.md` | 当前任务、已完成与证据、关键发现、未完成与阻塞、下一步、相关位置 | 仅该 agent | 交接前、有重要发现时 |

- STATE 保持简洁，只留对未来工作仍有意义的信息；重要结果指向真实文件、实验记录或提交；不重复保存完整实验数据；可以正常修改、更新和精简旧内容（历史靠 Git 追溯）；不必每次 commit 更新。科研项目明确区分**已验证事实 / 当前假设 / 未验证结论 / 已推翻或替代的结论**。
- TASKS 用简单表格或短条目，状态只用 `todo / doing / blocked / done`。单 agent 接续不必填资源分配表；多 agent 并行要能识别明显冲突（负责人、范围、主要文件、依赖）。任务状态是记录，**不是进程锁**。
- Agent 记录按 `assets/AGENT.md` 的六个小节写；长期使用时把旧任务压成摘要，重要结果靠原始文件和 Git 追溯，不保留流水账。同一 agent 的不同会话可继续维护自己的文件；不同运行实例可能同时工作时，用可区分实例 ID 的文件，避免互相覆盖。

**不记录**：每次工具调用、每条终端命令、中间思考、每次文件编辑、重复实验输出、模板化风险声明。重要失败只记原因、证据位置、是否值得重试。

## 认领与执行

1. 依次读 STATE → TASKS → 自己的 `agents/<id>.md`（接续时加读前任记录）→ 核对实际代码与结果文件。信息够就不继续展开。
2. 在 TASKS 标 `doing`，写负责人与范围。发现别人的 `doing` 与自己重叠，先按文件/资源协调；无法确认就暂停重叠部分，做能独立完成的部分。不得编造“已协商”，不得根据旧日志断言远程作业仍在运行。
3. 正常执行：**允许修改代码、改写论文、删除错误内容、更正结论、更新状态**。Git 历史提供追溯，不要求“只增不减”。
4. 事件驱动更新记录，不按固定间隔：完成有意义阶段、得到重要结果、重大失败或阻塞、重要决策、交接前、用户要求同步时。一次只更新必要文件：项目级结论进 STATE，任务状态进 TASKS，执行与交接进自己的 agent 记录；同一结果不重复写三份，靠相对链接关联。
5. 不根据文件存在断言实验成功；重要当前状态必要时核实实际文件、进程或证据。

## 两种协作模式

按**是否同时运行 / 是否共享物理工作目录 / 是否有重叠写入 / 是否需要独立分支**选择，不按 agent 名称硬编码。

**模式 A：同目录接力（默认）**。多个 agent 先后操作同一项目目录，不要求各自建分支或 worktree，不要求固定间隔同步。唯一硬前提：**同一物理 Git 工作目录中的 Git 写操作（checkout / add / commit / pull / rebase）必须串行**；不要为了方便同步清理别人的未提交修改。无法保证串行时，改用独立工作区。

**模式 B：并行**。真正同时做独立任务时，用同一 GitHub 仓库 + 不同任务分支 + 独立 worktree/clone + 明确的文件与资源分工。Git 正常合并；出现冲突时检查冲突的实际内容，不得简单采用某一方版本覆盖别人的工作；无法安全处理就停下并记录。

## GitHub 同步

默认就是**正常 commit、push；需要合并时用标准 Git 流程**。没有自动合并脚本，也没有“只增不减”判定。

1. 同步前看 `git status` 与 `git diff --cached --stat`；只显式 `git add -- <本次明确产物>`，**不用 `git add .` / `-A`**，不把未跟踪文件一股脑加入。
2. 检查上传范围：凭证、Token、密钥、隐私数据不上传；大型数据、模型权重、缓存未经确认不上传（可记录存放位置与获取方式）。
3. commit 后 push，用 `git ls-remote` 确认远端 SHA 与本地 HEAD 一致才算「已同步」；只有本地 commit 写「未同步」。
4. push 被拒：保留本地提交，fetch 查清原因后正常合并或 rebase；网络失败最多一次即时重试，仍失败记录未同步 SHA 与恢复命令，交接时再试。
5. 无冲突的正常变更按标准 Git 合并；冲突看实际内容再处理。不自动删除别人的分支，不重写远端历史。

## 交接与可复现性

交接：更新自己的 agent 记录（下一步要具体到可执行）→ TASKS 标 `done` / `blocked` → 项目级共识有变才更新 STATE → 同步 → 在回复里给出入口链接、完成/未完成事项、下个 agent 的第一步。

重要科研结果仍要可复现：实验代码、关键配置、数据与划分、随机种子、指标、原始结果或证据位置、必要复现说明，保存在项目原有实验目录或记录系统里；交接文档只需能定位它们。放不进 GitHub 的大文件记录位置、获取方法与必要校验信息，不强制为所有文件生成哈希清单。

## 安全边界

1. 不 force push；不自动删除分支；不重写远端历史；不改 Git 全局配置。
2. 不覆盖其他 agent 的工作、未提交修改或已暂存文件；共享脏工作区不做 `checkout` / `stash` / `reset --hard` / `git clean`。
3. 不上传凭证、密钥、隐私数据；大文件未经检查不上传。
4. 未确认结果不写成已验证结论；本地提交 ≠ 远端同步；合并成功 ≠ 科研验收。
5. 无法同步时保留本地工作并记录原因。

## 最小工作流示例

**同目录接力**

1. Agent A 进入项目：读项目入口 → `collaboration/STATE.md` → `TASKS.md` → `agents/codex.md`。缺少协作文档时，按「先发现，再复用」只补必要模板。
2. A 在 TASKS 标 `doing`、写范围，做实验，结果留在原有 `experiments/`；更新 STATE 的 Verified 与自己的 agent 记录（下一步写清可执行命令），正常显式 stage + commit + push，并确认远端。
3. Agent B 进入：同样只读这三份文件加 A 的记录 → 核对 `experiments/` 中实际结果 → 从 A 的「下一步」继续，把任务标 `done` 或 `blocked`。
4. B 不重建目录、不生成清单、不新建分支；只有状态或分工变化时才更新对应文档。

**并行**：A 与 B 在独立 worktree 同时工作时，各在 TASKS 写明 Scope（例如 `experiments/` 与 `paper/`），分别提交到自己的分支；合入前 fetch + 正常 merge，无冲突即合并，有冲突检查实际内容后再处理。

**不使用**：单人一次性改动、只需一次普通 commit、没有跨 agent 接续需求时，直接按正常流程做，不必启用本 skill。

## 模板

`assets/STATE.md`、`assets/TASKS.md`、`assets/AGENT.md` 只是起点，按项目需要删改，不强制填满所有小节。
