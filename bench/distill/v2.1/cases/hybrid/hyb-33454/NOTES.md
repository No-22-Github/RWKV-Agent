## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
28→31、22→24、36→40、32→35；用户要求食物恢复 36/32。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 把 menu.md 里所有价格上调 10%，四舍五入到整数。
2. 麻烦问下：把 menu.md 里所有价格上调 10%，四舍五入到整数。
3. 把 menu.md 里所有价格上调 10%，四舍五入到整数。（简单说就行）
4. 你好，把 menu.md 里所有价格上调 10%，四舍五入到整数。
5. 还有件事：把 menu.md 里所有价格上调 10%，四舍五入到整数。
