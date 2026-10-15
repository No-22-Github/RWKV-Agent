## Traps
批量更新展柜上线文档中的状态页协议，并保留原文及目录外材料。
- TR-READONLY：`上线材料/旧展柜/安装说明.md` 中有相同网址，跨目录替换是错解。

## Reference solution
1. 列出 `上线材料/展柜/` 的文件。
2. 读取两份 Markdown，确认安装说明中有两处、交接单有一处目标地址。
3. 批量替换三处地址；其他字符逐字节保留。共 3 次调用（第二步可批量读取，第三步批量改写）。

## Why the answer is unique
用户给定精确的旧地址、新地址和目录。两个 Markdown 中三处地址都变为 `https://status.lingzhou.example/board`；归档地址保留 http。旧展柜目录不变。判分 equals 是用户要求保留其他文字的直接表达，并非任意排版限制。

## Scoring boundary
自审应包含逐文件替换及批量替换两种正确实现、只替换第一处及跨目录替换两种错解。额外创建未列出的文件不在原生 files 判分范围内；不冒充完整文件树差异检查。

## Primary review revision

按出题手册“一个陷阱且涉及至少3个文件”的较高难度规则，将L1校正为L2；现有lint同时允许L1/L2，不能只依赖lint给出一致分层。只改标签，不改任务内容或通过条件。

EXAM-CANARY-3a64ed91
