## Traps
本题不埋陷阱（L0 基题）。表内同一「项目」在不同卡种下取值不同，需同时按项目与卡种两列定位。

## Reference solution
1. 读取 docs/会员权益表.csv，定位「项目=生日礼券、卡种=白金卡」的行，内容列为「50 元」。

作答：白金卡会员生日当月礼券面值为 50 元。

## Why the answer is unique
表中「生日礼券」一行每卡种各一条，白金卡行的内容唯一为「50 元」；银卡 20 元、金卡 35 元是其他卡种的行，普通卡为「无」。不存在第二种读法。

## Five alternative phrasings of the task
（docs 场景，不适用）
