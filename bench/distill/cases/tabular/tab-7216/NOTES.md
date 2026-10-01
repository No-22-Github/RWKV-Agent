## Traps
- TR-DUPROW: 导出重试把城北网点的 3 行整行重复写回（工单号相同、逐列相同）。按行数计会得到 38；README 写明工单号相同即同一笔，按工单号去重后为 35 笔。
- LNG: 城北网点的行段集中在导出尾部、超出 read_file 的 64 KB 截断线。

## Reference solution
1. read_file README.md：重试行同工单号，按工单号计数。
2. search_text「城北网点」定位行段（尾部）。
3. read_lines 读取该行段。
4. 按工单号去重计数，得 35；终答只报数字 35。

## Why the answer is unique
decoy 38 把重复写出的行当成了不同工单；重复行与原行逐列相同、工单号相同，没有任何读法能把它们算成不同的工单。城北网点行被网点精确相等过滤唯一确定。答案唯一为 35。
