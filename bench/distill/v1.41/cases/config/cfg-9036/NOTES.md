## Traps
- TR-DECOY: the root 限流.toml says qps = 500. Each bash call starts at /workspace, so a turn-2 `cat 限流.toml` after a turn-1 `cd 服务/风控` reads the root file.
- Turn 1 asks for a cd so the path actually carries the cd; a path without a turn-1 bash cd still passes but is not M9f coverage.

## Reference solution
Turn 1: bash `cd 服务/风控 && ls` -> 限流.toml, main.go.
Turn 2: bash `grep qps 服务/风控/限流.toml` (full path from /workspace) -> qps = 85.
Final answer turn 2: 风控服务的 qps 是 85（服务/风控/限流.toml 覆盖了根目录默认的 500）。

## Why the answer is unique
The question is about the file inside 服务/风控.
