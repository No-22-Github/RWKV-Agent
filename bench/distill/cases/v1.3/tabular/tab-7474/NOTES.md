## Traps
- TR-SIGN：冲销列以负数记入，只对应收列求和（忽略冲销）会得 183549.91；README 写明账面应收余额是应收与冲销两列之和，冲销的负号自带减向。

## Reference solution
1. 读 README.md：账面应收余额 = 应收 + 冲销，冲销以负数记入。
2. 查询：{"path":"data/receivables_2026-08.csv","operation":"sum","field":"应收"} 与 {"operation":"sum","field":"冲销"}，相加得 181062.79。
3. 终答只给数字 181062.79。

## Why the answer is unique
README 把余额定义成两列之和，冲销列的负号使求和自然成为减项；忽略冲销或再把冲销当减数都会与定义矛盾。答案唯一为 181062.79。
