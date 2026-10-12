## Traps
- TR-DECOY: the root README.md says SHA1 (and v1 says MD5). A turn-2 `cat README.md` after a turn-1 `cd 文档/接口/v2` reads the root file because each bash call starts at /workspace.
- Turn 1 asks for a cd so the path carries it; a path without a turn-1 bash cd is not M9f coverage.

## Reference solution
Turn 1: bash `cd 文档/接口/v2 && ls` -> README.md, 示例.json.
Turn 2: bash `cat 文档/接口/v2/README.md` (full path) -> 签名算法: HMAC-SHA256.
Final answer turn 2: v2 的 README.md 写的签名算法是 HMAC-SHA256（根目录 README 的 SHA1 是总览里的旧说法）。

## Why the answer is unique
The question is about the README.md inside 文档/接口/v2.
