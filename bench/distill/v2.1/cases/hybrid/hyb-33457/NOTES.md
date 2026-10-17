## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
先把 2 条已勾选项移走；之后放回原位，两个文件等于原样。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 把 todo.md 里已完成的条目移到 done.md 的末尾。
2. 麻烦问下：把 todo.md 里已完成的条目移到 done.md 的末尾。
3. 把 todo.md 里已完成的条目移到 done.md 的末尾。（简单说就行）
4. 你好，把 todo.md 里已完成的条目移到 done.md 的末尾。
5. 还有件事：把 todo.md 里已完成的条目移到 done.md 的末尾。
