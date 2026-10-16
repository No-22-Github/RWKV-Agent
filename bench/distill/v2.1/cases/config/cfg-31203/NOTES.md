## Traps
- TR-ABSENT: session_timeout 在被问的范围内没有定义。
- TR-DECOY: dev has session_timeout = 600; prod only has the similar-looking idle_timeout = 90.

## Reference solution
Read worker.prod.toml: no session_timeout, only idle_timeout.

## Why the answer is unique
worker.prod.toml does not define session_timeout (only idle_timeout = 90, a different setting); the 600 belongs to the dev file.
