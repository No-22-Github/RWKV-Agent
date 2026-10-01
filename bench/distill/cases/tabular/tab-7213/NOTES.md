## Traps
- TR-NEARNAME: FT-3306 旁边并排着后缀孪生码 FT-3306-B（黑磷化处理，README 写明是另一种零件，行段就在文件开头），而且 FT-3306-B 的行同样含 FT-3306 子串，检索会同时命中两类行。FT-3306-B 的在库合计为 1427.00；精确等于 FT-3306 的行合计为 1127.00。
- LNG: FT-3306 的行全部集中在导出尾部、超出 read_file 的 64 KB 截断线，整读拿不到。

## Reference solution
1. read_file README.md：part_code 是精确目录码，FT-3306 与 FT-3306-B 是两种零件。
2. search_text "FT-3306"：两类行都被命中，逐行核对 part_code 全值。
3. read_lines 读取尾部 FT-3306 的行段窗口。
4. 合计 qty_on_hand 得 1127.00；终答只报数字 1127.00。

## Why the answer is unique
decoy 1427.00 数的是另一种零件（-B 后缀）的在库量；part_code 逐行是全码，精确相等过滤或逐行核对下 FT-3306 不会混入 FT-3306-B。答案唯一为 1127.00。
