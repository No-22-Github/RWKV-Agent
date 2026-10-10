## Traps
- TR-TZ: node auth-eu-2 stamps CET (+01:00, README) while every window is given in UTC. Its four failed logins carry local 13:07:12-13:52:26, i.e. UTC 12:07-12:52 — outside the 13:00-14:00 UTC window. Comparing those local timestamps against the UTC window adds 4 rows and gives the recorded decoy 15; the true count is 11.

## Reference solution
1. Turn 1: read README.md (auth-eu-2 stamps CET), read logs/auth-login.log, count failed rows with UTC ts in [13:00, 14:00): auth-us-1 6 + auth-cn-3 5 = 11 (the eu-2 rows are UTC 12:xx). Answer: 11 failed.
2. Turn 2: failed rows per node across the UTC day: auth-us-1 9, auth-cn-3 8, auth-eu-2 4. Answer: auth-us-1.
3. Turn 3: auth-us-1's /v2/login failures that day: 5 (13:01:12, 13:07:44, 13:12:26, 13:21:03, 13:29:45). Answer: 5 failed.
4. Turn 4: restrict to [08:00, 20:00) UTC: auth-cn-3 7, auth-us-1 6, auth-eu-2 4. Answer: auth-cn-3.
5. Turn 5: auth-cn-3's last failed login of the day is 22:58:41. Answer: 22:58 (22:58:41).

## Why the answer is unique
The README pins which node deviates from UTC, so each row has exactly one UTC timestamp and the windows are unambiguous; the naive reading of eu-2's local stamps is the recorded decoy. Per-node totals (9-8-4), the /v2 subset of the leader (5 of its 9), the business-hours ranking (7-6-4) and the last row of the new leader all follow from the same normalized timestamps, and no tie occurs anywhere.
