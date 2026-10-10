## Traps
- TR-DECOY: 1 号岸桥有完全相同的一行。 Target line: `停机风速 = 20   # m/s，十级风前` ([岸桥2号]).

## Reference solution
1. No ticket: the new value is in the prompt.
2. Read 码头/岸桥.toml; locate the target line `停机风速 = 20   # m/s，十级风前`.
3. replace_lines that single line with `停机风速 = 18   # m/s，十级风前` (only 20 -> 18).
4. Read 码头/岸桥.toml back and confirm only that line changed.
Final answer: '已把 码头/岸桥.toml 里的 停机风速 改成 18，注释和缩进没动。'. Criteria: file equals the expected content exactly.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
