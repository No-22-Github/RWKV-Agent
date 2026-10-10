## Traps
- TR-DECOY: 地址缓存的最大条数也是 20000，按数值全文替换会误伤；且每行末尾逗号要保留。
- replace_lines must cover the whole run of 2 lines (start_line 4, end_line 5) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 配置/缓存.json; the target lines are 4-5.
2. replace_lines start_line 4, end_line 5 with:
       "用户": { "ttl": 900, "最大条数": 30000 },
       "券": { "ttl": 60, "最大条数": 1500 },
3. Read 配置/缓存.json back to confirm.
Final answer, one sentence then DONE on its own line: 已改 配置/缓存.json 第 4–5 行，共 2 行，改完回读确认无误。 / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
