## Traps
- TR-DECOY: data/charter_log.csv carries "Deep Sea Lite" beside the target "Deep Sea". Counting the Lite rows (or both) gives 13. June and August bookings are further distractors.

## Reference solution
1. data_query: {"path":"data/charter_log.csv","filter":{"booking_month":"2026-07","charter_type":"Deep Sea"},"operation":"count"} -> 17.
2. Reply with the number 17 only.

## Why the answer is unique
The decoy 13 is the Deep Sea Lite count, but the task names the Deep Sea charter, and the README fixes the naming: Deep Sea is the full-day offshore trip, Lite is a separate half-day trip. Every booking carries exactly one type. June and August rows fail the month condition. The answer is 17.
