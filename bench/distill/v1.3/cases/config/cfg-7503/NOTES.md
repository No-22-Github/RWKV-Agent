## Traps
- TR-DECOY: conf/scheduler.old.ini 里留着 retry_backoff_seconds = 600，粗读会把旧档值当成生效值。 A careless pass reports `600`.

## Reference solution
1. List conf/ and open scheduler.ini.
2. Read the queue and alerts sections for the live values.
3. Check scheduler.old.ini only to confirm it is the retired copy, then answer.

## Why the answer is unique
The live file is scheduler.ini and the old copy is the one carrying 600 with the -old webhook, so the effective backoff is 120 seconds and alerts post to the sched hook with quiet hours 23:00-06:30. Nothing in the live file supports any other reading.
