## Traps
- None. A stable-fact question; the user says no files are needed.

## Reference solution
No tool call. Answer in 1-2 sentences: it runs at 02:30 (2:30 AM, in the cron daemon's timezone) every Monday through Friday; fields are minute 30, hour 2, any day of month, any month, days of week 1-5. Criteria: zero calls, contains 2:30 and a Monday-to-Friday phrase.

## Why the answer is unique
Standard five-field cron syntax: minute, hour, day of month, month, day of week, where 1-5 is Monday to Friday.
