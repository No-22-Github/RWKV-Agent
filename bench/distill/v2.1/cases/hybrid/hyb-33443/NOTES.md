## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
三个文件 timeout 10→30；用户接受后要求全部改回，终态等于原样。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 把 svc 下三个 yaml 的 timeout 都改成 30。
2. 麻烦问下：把 svc 下三个 yaml 的 timeout 都改成 30。
3. 把 svc 下三个 yaml 的 timeout 都改成 30。（简单说就行）
4. 你好，把 svc 下三个 yaml 的 timeout 都改成 30。
5. 还有件事：把 svc 下三个 yaml 的 timeout 都改成 30。
