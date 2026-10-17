## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
Rename in both files; after accept, change fetchUser back to getUser in both so the tree equals the original.

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. Rename getUser to fetchUser in all the files under src.
2. 麻烦问下：Rename getUser to fetchUser in all the files under src.
3. Rename getUser to fetchUser in all the files under src.（简单说就行）
4. 你好，Rename getUser to fetchUser in all the files under src.
5. 还有件事：Rename getUser to fetchUser in all the files under src.
