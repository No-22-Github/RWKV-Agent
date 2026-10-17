## Traps
- Undo: the change from turn 1 is already on disk (user accepted it); reverting needs the earlier content, restoring too much or too little fails.

## Reference solution
第一轮改 maxmemory 为 1gb；用户接受后要求撤销，改回 256mb，其余不动。

## Why the answer is unique
Turn 1 makes the edit; turn 2 reverts all or part of it; final files equal expect.files (rules are relative to the initial fixture).

## Five alternative phrasings of the task
1. 把 conf/redis.conf 里的 maxmemory 调到 1gb。
2. 麻烦问下：把 conf/redis.conf 里的 maxmemory 调到 1gb。
3. 把 conf/redis.conf 里的 maxmemory 调到 1gb。（简单说就行）
4. 你好，把 conf/redis.conf 里的 maxmemory 调到 1gb。
5. 还有件事：把 conf/redis.conf 里的 maxmemory 调到 1gb。
