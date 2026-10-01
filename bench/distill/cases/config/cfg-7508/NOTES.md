## Traps
- TR-DECOY: docs/runbook.md 写着旧的 03:00 窗口和 14 天保留，粗读会拿旧数字作答。 A careless pass reports `03:00`.

## Reference solution
1. Read config/backup.yaml for target, schedule and retention.
2. Read docs/runbook.md and note it is marked stale.
3. Describe today's behavior using the config values.

## Why the answer is unique
The runbook is labeled stale and points at the config file for current values, so the 03:00 window and the 14-day retention are historical. backup.yaml states one target, one cron schedule starting 02:30, and retention_days 35, so the auditor answer is fixed.
