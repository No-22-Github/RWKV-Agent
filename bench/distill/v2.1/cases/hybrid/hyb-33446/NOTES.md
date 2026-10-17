## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
先改 69；用户接受后要求撤销并改 64，终态 basic,64。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 把 pricing.csv 里 basic 的价格改成 69。
2. 麻烦问下：把 pricing.csv 里 basic 的价格改成 69。
3. 把 pricing.csv 里 basic 的价格改成 69。（简单说就行）
4. 你好，把 pricing.csv 里 basic 的价格改成 69。
5. 还有件事：把 pricing.csv 里 basic 的价格改成 69。
