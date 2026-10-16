## Traps
- TR-ABSENT: 问题的后半部分（reply_to）查不到。
- TR-DECOY: sender 容易被拿来充当回复地址。

## Reference solution
sender 有；reply_to 没配。

## Why the answer is unique
读 config.ini：sender=noreply@corp.example；没有 reply_to。
