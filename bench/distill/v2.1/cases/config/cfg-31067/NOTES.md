## Traps
- TR-CLAIM: comma after the former last element; price 2 occurs for two items.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines
2. edit line 4 + insert
3. edit line 2
4. read back
5. read back the edited region and compare with the request

## Why the answer is unique
Final array has 4 items, 豆浆 4.
Final answer should mention: 茶叶蛋; 4; 茶叶蛋; 粢饭
