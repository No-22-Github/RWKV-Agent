## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
Update all three, then restore vendor/lib.go only.

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. Change the copyright year from 2025 to 2026 in all three Go files.
2. 麻烦问下：Change the copyright year from 2025 to 2026 in all three Go files.
3. Change the copyright year from 2025 to 2026 in all three Go files.（简单说就行）
4. 你好，Change the copyright year from 2025 to 2026 in all three Go files.
5. 还有件事：Change the copyright year from 2025 to 2026 in all three Go files.
