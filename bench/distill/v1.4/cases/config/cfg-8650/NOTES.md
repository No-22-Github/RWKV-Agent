## Traps
- TR-DECOY: 订单服务的块长得一模一样，只能改库存服务那三行。
- replace_lines must cover the whole run of 3 lines (start_line 9, end_line 11) and content must have 3 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 网关/上游.conf; the target lines are 9-11.
2. replace_lines start_line 9, end_line 11 with:
       server 10.2.4.31:8080 weight=4;
       server 10.2.4.32:8080 weight=1;
       keepalive 64;
3. Read 网关/上游.conf back to confirm.
Final answer, one sentence then DONE on its own line: 已改 网关/上游.conf 第 9–11 行，共 3 行，改完回读确认无误。 / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
