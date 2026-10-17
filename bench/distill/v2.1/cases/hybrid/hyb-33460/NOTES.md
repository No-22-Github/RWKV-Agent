## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
追加 a.md 内容到 b.md 并删除 a.md；之后重建 a.md 并还原 b.md。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 把 notes/a.md 合并进 notes/b.md（接在末尾），然后删掉 a.md。
2. 麻烦问下：把 notes/a.md 合并进 notes/b.md（接在末尾），然后删掉 a.md。
3. 把 notes/a.md 合并进 notes/b.md（接在末尾），然后删掉 a.md。（简单说就行）
4. 你好，把 notes/a.md 合并进 notes/b.md（接在末尾），然后删掉 a.md。
5. 还有件事：把 notes/a.md 合并进 notes/b.md（接在末尾），然后删掉 a.md。
