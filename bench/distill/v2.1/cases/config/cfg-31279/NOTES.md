## Traps
- TR-ABSENT: 问题的后半部分（default currency）查不到。
- TR-DECOY: London timezone tempts an answer of GBP.

## Reference solution
Language is set; currency isn't (timezone London is only a hint, not a setting).

## Why the answer is unique
Read settings.json: default_language en-GB; no currency key.
