## Traps
- TR-TZ: the log is stamped in UTC (README) while every window in the session is given in Beijing time (+08:00). Reading "14:00 到 15:00" straight off the log timestamps counts the UTC 14:00-15:00 rows (4) instead of the UTC 06:00-07:00 rows (9); 4 is the recorded decoy.

## Reference solution
1. Turn 1: read README.md (log clock is UTC, Beijing = UTC+8), read logs/smtp-delivery.log, convert Beijing 14:00-15:00 on 09-24 to UTC 06:00-07:00, count deferred rows: 9. Answer: 9 封.
2. Turn 2: of those nine, two come from rcpt=mailer-test@... (06:15:40, 06:44:49); excluding them leaves 7. Answer: 7 封.
3. Turn 3: Beijing 15:00-16:00 is UTC 07:00-08:00: 8 deferred rows. Answer: 8 封.
4. Turn 4: reason codes in that hour: 451 x5, 450 x2, 421 x1. Answer: 451.
5. Turn 5: Beijing 09-24 00:00-24:00 is UTC 2026-09-23T16:00 to 2026-09-24T16:00; mailbox busy rows inside: 16:12:44, 17:38:52, 17:52:16 (23rd), 01:12:56, 06:36:26, 06:52:12, 07:43:53, 07:51:16, 11:14:48 (24th) = 9. Answer: 9 封.

## Why the answer is unique
The README pins the log clock to UTC, so the Beijing windows have exactly one UTC counterpart and the row timestamps decide membership; the naive UTC reading is the recorded trap. Each row carries one status and one reason, the mailer-test rows are identified by their recipient prefix, and the mailbox-busy day window is bounded by the +8h shift, so every count has a single reading.
