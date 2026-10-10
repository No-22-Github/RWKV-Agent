## Traps
- TR-DECOY: 青椒炒蛋的鸡蛋和盐行与番茄炒蛋逐字相同，范围只能是番茄炒蛋那四行。
- replace_lines must cover the whole run of 4 lines (start_line 4, end_line 7) and content must have 4 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read 食谱/家常菜.md; the target lines are 4-7.
2. replace_lines start_line 4, end_line 7 with:
   - 番茄 3 个
   - 鸡蛋 4 个
   - 盐 3 克
   - 糖 8 克
3. Read 食谱/家常菜.md back to confirm.
Final answer, one sentence: 已改 食谱/家常菜.md 第 4–7 行，共 4 行，改完回读确认无误。 Criteria: file equals the expected text exactly.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
