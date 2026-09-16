## Traps
- TR-NEARNAME: README.md and docs/data_governance_notes.md both cite config/retention.yml as the place where watch-history rules used to live. No such file is on disk; the live file is config/history_retention.yaml. A model that answers from the prose without checking the listing gives config/retention.yml (the recorded decoy).

## Reference solution
1. list_files the workspace and see the actual config/ entries (call 1)
2. read README.md for the config layout and the retention history note (call 2)
3. read config/history_retention.yaml and confirm it holds the watch-history retention periods (call 3)
4. answer config/history_retention.yaml (call 4)

## Why the answer is unique
Exactly one .yaml file on disk defines retention periods (its first key is the retention block; playback.yaml and subtitles.yaml cover unrelated settings). The .yml path exists only in prose. No second YAML file on disk is a plausible candidate, so the path answer is unambiguous.
