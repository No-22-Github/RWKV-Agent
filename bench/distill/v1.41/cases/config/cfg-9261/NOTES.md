## Traps
- TR-READONLY: 数据源/_归档 stays as it is; `pool.size.min=10` is a look-alike key the README says never changes (`s/=10/=20/` or `s/pool.size=10/.../` without anchors also hits it).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find 数据源 -name '*.properties' | grep -v /_归档/ | xargs sed -i 's/^pool\.size=10$/pool.size=20/'`
2. bash: `grep -rn '^pool' 数据源`
Final answer: DONE (五个库的 pool.size 为 20).
Turn 2:
1. bash: `sed -i 's/^pool\.size=20$/pool.size=10/' 数据源/订单.properties && sed -i 's/^pool\.size=20$/pool.size=40/' 数据源/报表.properties`
2. bash: `grep -rn '^pool' 数据源`
Final answer: DONE (订单回 10，报表 40，其余 20).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 数据源连接池上限全部翻倍到 20（归档除外），再把订单库退回去、报表库提到 40
2. pool.size 10 改 20，之后订单恢复 10，报表设为 40
3. 各库连接池扩到 20，订单库不扩，报表库扩到 40
4. 把连接池上限 10 批量调成 20，订单还原，报表 40
5. Raise pool.size to 20 in all datasources, then put orders back to 10 and set reports to 40.
