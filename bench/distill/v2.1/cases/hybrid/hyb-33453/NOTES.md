## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
排序去重后，用户要求保留排序、恢复重复行：3 个 apple、2 个 banana。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. Sort the lines in names.txt alphabetically and remove duplicates.
2. 麻烦问下：Sort the lines in names.txt alphabetically and remove duplicates.
3. Sort the lines in names.txt alphabetically and remove duplicates.（简单说就行）
4. 你好，Sort the lines in names.txt alphabetically and remove duplicates.
5. 还有件事：Sort the lines in names.txt alphabetically and remove duplicates.
