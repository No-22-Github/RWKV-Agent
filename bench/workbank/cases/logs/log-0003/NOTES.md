## Traps
- TR-DATEFMT: the log mixes three timestamp styles (2026/09/01, 01-09-2026, Sep 1, 2026). Three in-window rejection lines are dash-dated (01-09-2026 11:47, 02-09-2026 02:19, 02-09-2026 13:52); reading dashes month-first turns them into Jan 9 / Feb 9, which drops them across the interval boundary and yields 4 instead of 7. The README pins the day-first convention for dash stamps.

## Reference solution
1. list_files (1)
2. read_file README.md, which states the collector timestamp convention (2)
3. read_file logs/carrier-webhook.log (3)
4. Parse each E_LABEL_REJECT stamp in its own style (slashes year-first, dashes day-first, month names US), keep Sep 1-2, reply 7 (4)

## Why the answer is unique
The interval is the calendar days Sep 1-2 inclusive. Under the documented convention exactly 7 rejection lines fall inside (3 on Sep 1, 4 on Sep 2). The two Sep 3 rejections stay outside under every reading of their stamps (03-09-2026 and Sep 3, 2026), and no other line kind matches the event code.

<!-- WORKBANK-CANARY-7c45e2b9 : this file must never enter training corpora -->
