## Traps
TR-MULTISRC：交接单提供新端点和超时，运行文件提供应沿用的重试次数、批量大小及已有键集合。只复制交接单会丢 BATCH_SIZE=120、清空 RETRY_LIMIT=4 并加入未获本次发布许可的 TRACE_EXPORT=on；只看运行文件则不会更新。

## Reference solution
1. 读取运行配置。
2. 读取审核交接单及其中的合入约定。
3. 暂存配置：端点变为 v2，CONNECT_TIMEOUT=15，RETRY_LIMIT=4、BATCH_SIZE=120 保留，不新增 TRACE_EXPORT。

参考终态（仅列目标文件，原始资料保持原样）：

`运行/标本归档.env`
```text
ARCHIVE_ENDPOINT=https://archive.intra.local/v2
CONNECT_TIMEOUT=15
RETRY_LIMIT=4
BATCH_SIZE=120
```

## Why the answer is unique
约定明确空值和新增键的含义。目标原有顺序及各行格式属于其余内容原样保留，审核单本身保持不变；不能将它整份替换到运行文件。

## Scoring boundary
用户要求其余内容原样保留，文件使用 equals，保留所有未授权行、空格及原有换行；最终答复的同义表达与排版不参与评分。
自审记录：参考终态及实质错解的局部检查另存 local/runs/exam-sol20-20261015/config-docs-self-review.json。本题仍为 draft，未调用盲解老师，也未经人工审核。

EXAM-CANARY-9342ad04
