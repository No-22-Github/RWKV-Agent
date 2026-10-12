## Traps
- TR-DECOY: the user names one file; a backup, old, example or other-environment copy carries a different value (600).

## Reference solution
1. read_file on the named file.
Final answer: rollout 的 timeout_seconds 是 900（deploy.toml.orig 里的 600 是旧值）。

## Why the answer is unique
The user names the file; only it holds the current value. The copy with another value is a decoy.
Why bash is not the tool here: one named file and one fact, the read tool is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.

## Five alternative phrasings of the task
1. 发布超时时间是多少秒？看 部署/deploy.toml 的 rollout 段。
2. deploy.toml 里 rollout 超时设成了几秒？
3. 部署/deploy.toml：rollout 的超时秒数？
4. 帮我看看 部署/deploy.toml，发布的 timeout_seconds 是多少。
5. rollout 段的 timeout_seconds 当前值是什么？
