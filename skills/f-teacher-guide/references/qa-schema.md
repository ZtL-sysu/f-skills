# QA Evidence Schema

Store a JSON record per distribution round with these fields:

```json
{
  "package": "english_root_name",
  "archive": {"path": "...zip", "sha256": "...", "member_count": 0},
  "real_machine": {
    "hardware": "...",
    "os": "...",
    "target_platform": "...",
    "conda_environment": "...",
    "started_at": "...",
    "finished_at": "..."
  },
  "path_contract": {"errors": [], "warnings": []},
  "execution": {
    "command_ledger": [
      {
        "step": 1,
        "command_index": 1,
        "command": "exact one-line student command",
        "exit_code": 0,
        "elapsed_seconds": 0.0,
        "evidence": "observable result",
        "real_gui": false
      }
    ],
    "resource_check": {"exit_code": 0, "summary": "..."},
    "build": {"exit_code": 0, "summary": "..."},
    "baseline": {"exit_code": 0, "metrics": {}},
    "parameter_sweep": {"levels": [], "exit_codes": [], "summary_table": "...", "trend_plot": "..."},
    "gui_steps": {"required": 0, "visually_verified": 0, "evidence": []},
    "acceptance": {"exit_code": 0, "summary": "..."}
  },
  "docx": {
    "page_count": 0,
    "a11y": {"high": 0, "medium": 0, "low": 0},
    "visual_pages_checked": 0,
    "visual_issues": []
  }
}
```

Acceptance requires no path errors, every displayed command represented exactly once in the ledger, all required execution exit codes zero, every parameter level present, required summary/trend evidence present, all required GUI states visually verified on the target platform, accessibility counts zero unless explicitly waived, and `visual_pages_checked == page_count` with no unresolved visual issues.
