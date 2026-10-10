## Traps
- None. Stable cron syntax; the jobs list is a decoy the user forbids opening.

## Reference solution
No tool call. Answer in 1-2 sentences: fields are minute, hour, day-of-month, month, day-of-week, so it runs at 22:00 (10 PM) every Sunday; 0 in the day-of-week field means Sunday. Criteria: zero calls, contains Sunday and the time as 22:00 or 10 PM.

## Why the answer is unique
Standard five-field cron: 0 = Sunday, 22 = the 10 PM hour. The answer is fully determined by the expression in the prompt.
