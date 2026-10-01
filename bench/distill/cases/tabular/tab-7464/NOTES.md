## Traps
- TR-NEARNAME：表里有两个近名客户「望江轮胎」与「望江轮胎股份」，按前缀把两家并起来会得 12；README 写明两者是独立客户，账务互不合并。

## Reference solution
1. 读 README.md：望江轮胎与望江轮胎股份是两个独立客户。
2. 查询：{"path":"data/tire_orders_2026-08.csv","filter":{"客户":"望江轮胎"},"operation":"count"}，得 7.0。
3. 终答只给数字 7.0。

## Why the answer is unique
客户列是精确字符串，README 又把两家定为互不合并的独立主体，前缀合并的读法与文件自身说明矛盾。计数口径为行数，答案唯一为 7.0。
