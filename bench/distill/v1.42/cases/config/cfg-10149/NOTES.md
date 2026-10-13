## Traps
- TR-DECOY: the root 限流.yaml says 200. Every bash call starts at the workspace root, so a turn-2 `cat 限流.yaml` after turn 1's `cd 服务/订单` reads the root copy.

## Reference solution
Turn 1: bash `cd 服务/订单 && ls` -> lists 入口.go among others.
Turn 2: read 服务/订单/限流.yaml by its full path (read tool or bash) -> 75.
Final answer turn 2: 订单服务的每秒请求上限是 75（服务/订单/限流.yaml，根目录默认是 200）。

## Why the answer is unique
The question is about the file inside 服务/订单.
