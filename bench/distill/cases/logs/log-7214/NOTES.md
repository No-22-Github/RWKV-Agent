## Traps
- TR-NEARNAME: 日志里同时有 edge-cw-01 与 edge-cw-l01（灰度小写 L，不是数字 1），后者当天有 12 条 ERROR。把两个节点混在一起会得到 43；只数 edge-cw-01 的 ERROR 才是 31。

## Reference solution
1. 读 README.md：行格式与两个节点名的区别。
2. 检索「节点=edge-cw-01」，在命中处附近的行段里逐条核对级别。
3. 只保留 ERROR 级的行，不把 edge-cw-l01 的行计入。
4. 共 31 条。

## Why the answer is unique
节点名是行内字段，README 写明两个名字互不相干；级别字段决定了只有 ERROR 计入。答案是 31。
