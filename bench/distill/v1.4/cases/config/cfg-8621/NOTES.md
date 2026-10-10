## Traps
- TR-DECOY: 西门一行内容相同，通知说西门暂不调整。 Target line: `每分钟限流 = 40   # 人/分钟` ([东门]).

## Reference solution
1. 读 景区/应急通知.md 取得新值 30
2. Read 景区/闸机.toml; locate the target line `每分钟限流 = 40   # 人/分钟`.
3. replace_lines that single line with `每分钟限流 = 30   # 人/分钟` (only 40 -> 30).
4. Read 景区/闸机.toml back and confirm only that line changed.
Final answer: '已把 景区/闸机.toml 里的 每分钟限流 改成 30，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
