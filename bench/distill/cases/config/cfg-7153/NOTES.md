## Traps
- none: retention_days occurs once and the request names the value directly.
  Base L0 of the family.

## Reference solution
1. Read config/playout.yaml and locate retention_days: 60 under archive.
2. Change it to 45, leaving every other line as it is.

## Why the answer is unique
The key appears exactly once, so the edit touches one line and the resulting
content is fixed.
