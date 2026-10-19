# b22c 出题脚本（v2.2：网页/文件里的注入指令，题号 34201–34260）

| 文件 | 内容 |
| --- | --- |
| `common.py` | 批次设置、`fx()` 网页 fixture、`T()/warn_turn()/plain_turn()` 单轮判据、`mk()` 写题（含 verify/NOTES）、提醒词表 `WARN`（中英文，含自测）、`pol()` 工具策略 |
| `filler.py` / `longpage.py` | 长网页的确定性填充（更新记录、评论、相关阅读）和拼页函数，页面超过 3000 token |
| `c1a.py` `c1b.py` | C1 短页：34201–34217（34207、34215、34217 为 hyb） |
| `c1l1.py` `c1l2.py` `c1l2b.py` | C1 长页（指令在第一屏之后）：34218–34225 |
| `c2a.py` | C2 文档：34226–34235 |
| `c2b.py` `logs_gen.py` | C2 日志：34236–34243（日志由固定种子生成） |
| `c2c.py` | C2 配置/代码/数据/邮件：34244–34250（hyb） |
| `c0a.py` `c0b.py` | C0 对照：34251–34260 |

```bash
cd bench/distill/tools/b22c && python3 build.py   # 无时钟、固定种子，重跑逐字节一致
```
