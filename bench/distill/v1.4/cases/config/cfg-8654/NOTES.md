## Traps
- TR-DECOY: 短信、推送两段键后缀和邮件完全对应，改错段就挂。
- replace_lines must cover the whole run of 4 lines (start_line 8, end_line 11) and content must have 4 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read config/通知.env; the target lines are 8-11.
2. replace_lines start_line 8, end_line 11 with:
   MAIL_PROVIDER=ses
   MAIL_RATE_PER_MIN=200
   MAIL_RETRY=3
   MAIL_TIMEOUT_MS=5000
3. Read config/通知.env back to confirm.
Final answer, one sentence: 已改 config/通知.env 第 8–11 行，共 4 行，改完回读确认无误。 Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
