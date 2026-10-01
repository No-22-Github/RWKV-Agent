## Traps
- TR-MISSING: crew_chief 列混写三种「无人签核」形态——空、NA、短横线（README 写明）。Larkspur Loop 的 38 个班次里有 9 个无人签核，按行数计会得到 38；有负责人记录的班次为 29。
- LNG: Larkspur 的行段集中在导出尾部、超出 read_file 的 64 KB 截断线。

## Reference solution
1. read_file README.md：无人签核时 terminal 留空、写 NA 或短横线。
2. search_text "Larkspur Loop" 定位行段（尾部）。
3. read_lines 读取该行段，逐行核对 crew_chief。
4. 计有负责人记录的班次，得 29；终答只报数字 29。

## Why the answer is unique
decoy 38 把无人签核的班次当成了有负责人；三种占位形态在 README 里写明、且与任何人名不重合，Larkspur 行被 trail 精确相等过滤唯一确定。答案唯一为 29。
