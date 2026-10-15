## Traps
- TR-NOTOOLNEED：本次素材总量、份数和单位口径已在消息里，工作区里的上次分发清单.csv记录每包640MiB，不能替代本次数据。
## Reference solution
不调用工具；3.5×1024÷4=896，答“每包896 MiB”。ref_calls=0。
## Why the answer is unique
消息明示二进制单位关系，四包等分，不考虑压缩或封装变化。每包896MiB；875是按1000换算的错误结果，640是上一批数据。
## Scoring boundary
“896 MiB”“每包大小为896MiB”及“896.0MiB”都应通过；875、640、3584（总量未等分）应失败。tools=[]与require_active_no_call检查实际零调用，旧文件unchanged。数字in_text不能排除列出多个候选又带896的含糊回答。改坏旧文件后verify答案不变应被记录为检查器边界，不人为读旧文件或增加断言。

## Final teacher result

最终版DeepSeek算对每包896MiB，但调用calculator，违反tools=[]及require_active_no_call。首轮未调用工具时曾通过；这是工具决策波动，保留判分。

EXAM-CANARY-c81f530d
