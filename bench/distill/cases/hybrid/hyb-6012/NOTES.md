## Traps
- TR-AMBIG: the request names the Lark while runs/april-2026.csv holds two candidates, White Lark and Red Lark. Reading it as Red Lark gives 18; the request was settled on White Lark, giving 32 (from runs/april-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the Lark but the workspace holds two candidates, White Lark and Red Lark, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds runs/april-2026.csv and README.md.
3. read runs/april-2026.csv and take the total of the drops column for White Lark: 32.

## Why the answer is unique
The decoy 18 belongs to Red Lark; it answers a different candidate, and the request was settled on White Lark before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 32.

## Five alternative phrasings of the task
1. bramhope garden centre lark deliveries april 2026
2. delivery runs for red lark and white lark
3. drops per van bramhope april
4. van recharge sheets delivery counts
5. april deliveries by the two larks
