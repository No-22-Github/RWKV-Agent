# b23g 出题脚本（v2.3：答案在第一屏之后，题号 35501–35540）

`python3 build.py` 写 40 题到 `bench/distill/v2.3/cases/{docs,logs,config,code}/`，固定种子，重跑逐字节一致。

| 文件 | 内容 |
| --- | --- |
| `fill.py` | 填充内容生成器（散文文档、变更记录、会议纪要、日志、yaml/ini/toml/properties、py/go/js 代码）和 `compose` |
| `common.py` | `make()`：写 case/verify/NOTES；构建时断言 G1 答案行 >230、干扰行 <150，G0 答案行 <60、深处近似行 >230 |
| `g1_docs.py` `g1_logs.py` `g1_cfg.py` `g1_code.py` | G1 doc-35501…08、log-35509…16、cfg-35517…23、code-35524…30 |
| `g0.py` | G0 对照 doc-35531…33、log-35534…35、cfg-35536…38、code-35539…40 |

判据：G1 `output_contains`（或 `output_contains_any`）放深处的值，`output_excludes` 放第一屏的干扰值，case 级 `max_calls: {read_file: 4}`；G0 `max_calls: {read_file: 1}`，excludes 放深处的近似值。首轮 `required_tools: [read_file]`。
