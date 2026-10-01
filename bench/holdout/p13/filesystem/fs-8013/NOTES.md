## Traps
- TR-DECOY: icons/01-hero.json.bak（改版前备份）比任何 .json 资产都大， README 写明 .bak 是备份副本、不算可用资产。直接按文件大小全目录取最大会答 01-hero.json.bak。可用资产里 01-hero.json（单行 JSON，最长）最大，其后是 02-badge.json、03-arrow.json。

## Reference solution
1. 列出 icons 目录：01-hero.json、01-hero.json.bak、02-badge.json、03-arrow.json，读 README.md 的资产口径。
2. 排除 .bak，比较三个 .json 资产的内容大小。
3. 最大的是 01-hero.json。

## Why the answer is unique
「可用的资产」按 README 的口径排除 .bak；剩余三个 .json 的大小两两不同（hero 明显大于 badge、arrow），最大者唯一。.bak 虽然最大但它不是资产，与口径冲突。答案唯一为 01-hero.json。
