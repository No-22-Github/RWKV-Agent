## Traps
- TR-NOTOOLNEED：全部本场数据已在消息中；工作区的上周餐盒复盘.csv写的是117，查旧文件既无必要又会带来错数。
## Reference solution
不调用工具；按消息计算126+18-11-9=124，直接答“来宾实际用了124份”。ref_calls=0。
## Why the answer is unique
预订和现场增加是全部供应量，剩下与志愿者用餐都不属于来宾；实给来宾124份。工作区记录明确为上周，不适用于本场。
## Scoring boundary
自然答案“124份”“来宾用了124份餐盒”均应通过；123、133（未扣志愿者）和117均应失败。tools=[]与require_active_no_call要求实际不调用工具，源文件unchanged。数字in_text仍可能接受同时列出124和错误结论的回答，这是现有判分边界。bank verify改坏无关旧文件而答案不变是正确行为，不添加无关断言伪造sabotage通过。

EXAM-CANARY-482ad1e6
