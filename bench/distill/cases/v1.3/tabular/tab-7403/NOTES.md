## Traps
- TR-DECOY: in service/visit_log.csv September 2026 holds 30 rows, only 6 of them Valve; the other 24 are Pump, Sensor and similar issues, with more rows and larger readings. Averaging the whole month gives 6.525 - the mixture the task does not ask for. The Valve visits average 3.875 hours.

## Reference solution
1. Aggregate: {{"path":"service/visit_log.csv","filter":{{"issue_type":"Valve","visit_month":"2026-09"}},"operation":"avg","field":"downtime_hours"}} gives 3.875.
2. Reply with the number 3.875 only.

## Why the answer is unique
The decoy 6.525 mixes every issue type into the average, but the task limits the visits to a Valve issue, so the other rows do not qualify. Rows from other months fail the visit_month filter. The answer is 3.875.
