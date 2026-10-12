## Traps
- TR-DECOY: the [worker-canary] section has the same key with 512; limits.toml.old says 256.

## Reference solution
1. read_file deploy/limits.toml
Final answer: [worker] 段的 memory_mb 是 768（canary 段是 512，不是 worker 本身）。

## Why the answer is unique
The user names deploy/limits.toml; only its live line holds the answer. [worker-canary] shares the key (512) and limits.toml.old is stale (256).
Why bash is not the tool here: one named file and one fact, read_file is the direct read. The turn forbids bash.

## Five alternative phrasings of the task
1. 看一下 deploy/limits.toml，worker 的内存上限（MB）设的是多少？
2. deploy/limits.toml 中 worker 组件的 memory_mb 写的几？
3. 按 deploy/limits.toml，[worker] 能用多少 MB 内存？
4. worker 的内存配额是多少？以 deploy/limits.toml 为准。
5. 帮我查 deploy/limits.toml：[worker] 段 memory_mb。
