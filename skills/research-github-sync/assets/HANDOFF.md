# Handoff: <task_id> / <agent_id>

- Updated: <ISO8601 with timezone>
- Branch: agent/<task_id>/<agent_id>
- Work status: <in_progress | completed | blocked | failed>
- Protocol: <relative path and SHA-256>
- Latest checkpoint: <relative link>
- Sync: <remote branch + verified commit, or local-only commit + reason>
- Auto-merge: <merged + default-branch commit | refused + reason | not attempted>

## Established

<completed work with evidence links; distinguish checked results from hypotheses>

## Remaining

<missing evidence, failed gates, unavailable dependencies>

## Live jobs

<provider, actual job/process ID, last observed state/time, query command; none if none>

## Resume

<exact working directory/relative paths, next command, required inputs and stop condition>
