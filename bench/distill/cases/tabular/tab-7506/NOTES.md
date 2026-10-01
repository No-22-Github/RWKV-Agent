## Traps
- TR-DECOY: data/class_sessions.csv carries "Yoga Flow Restore" beside the target "Yoga Flow". Averaging the Restore sessions (or both) gives 11.2105. May and July sessions are further distractors around the June target.

## Reference solution
1. data_query: {"path":"data/class_sessions.csv","filter":{"session_month":"2026-06","class_name":"Yoga Flow"},"operation":"avg","field":"attendees"} -> 10.2083.
2. Reply with the number 10.2083 only.

## Why the answer is unique
The decoy 11.2105 is the Yoga Flow Restore average, but the task names Yoga Flow, and the README fixes the naming: Flow is the vinyasa class, Restore is a separate slow class. Every row carries exactly one class name, so no reading mixes them. May and July rows fail the month condition. The answer is 10.2083.
