## Traps
- TR-DECOY: ExecStart 紧挨在被改范围上方，范围从 Restart 行开始，不能把它盖掉。
- replace_lines must cover the whole run of 3 lines (start_line 7, end_line 9) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read systemd/export.service; the target lines are 7-9.
2. replace_lines start_line 7, end_line 9 with:
   Restart=always
   RestartSec=10
   LimitNOFILE=65536
3. Read systemd/export.service back to confirm.
Final answer, one sentence: 已改 systemd/export.service 第 7–9 行，共 3 行，改完回读确认无误。 Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
