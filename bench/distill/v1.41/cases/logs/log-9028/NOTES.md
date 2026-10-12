## Traps
- TR-TRUNC: audit.log is ~247KB, past the 64KB read cap and the 8KB command output cap; the first 64KB only holds 92 matching lines.
- TR-DECOY: lisiyu, lisi-bot and LOGIN_FAIL_LOCKED all contain the target strings as substrings (a substring match gives 951).

## Reference solution
1. bash: `grep -c ' 用户=lisi 动作=LOGIN_FAIL 来源' 审计/audit.log`
Final answer: lisi 一共登录失败 308 次（动作恰好为 LOGIN_FAIL，lisiyu、lisi-bot 和 LOGIN_FAIL_LOCKED 不算）。

## Why the answer is unique
User and action are exact key=value tokens; counting over the whole file gives one number.
