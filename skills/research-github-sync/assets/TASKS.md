# Tasks

| Task | Status | Owner | Scope / files | Depends on |
|---|---|---|---|---|
| <任务> | todo | <agent_id> | <主要文件或目录> | <任务或 none> |

状态只用 `todo / doing / blocked / done`。

单 agent 接续可只留任务与状态。多 agent 并行时写清负责人、范围、主要文件和依赖，以便识别明显冲突；状态只是协作记录，不是进程锁，`doing` 不代表进程仍在运行。任务完成后标 `done`，并在结果或 agent 记录里给出证据位置。
