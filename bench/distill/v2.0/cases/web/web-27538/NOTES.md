## Traps
- 无陷阱（L0 基题）。同一页里还有常用密码 20 组、临时密码 10 把两个数，
  题面问的是指纹容量。

## Reference solution
1. 取题面给出的 https://help.songlan.example/capacity 页面（web_fetch）（1）
2. 读「指纹」一行：最多可录入 30 组指纹，作答（2）

## Why the answer is unique
页面「指纹」「门禁密码」「临时密码」三行各对应一个上限，题面问指纹，
只有 30 一个值与之对应；20 是常用密码、10 是临时密码，均不匹配题面问法。

## 正确答案
30

## Five alternative phrasings
1. 松阑智能门锁 指纹 上限
2. 松阑门锁 最多多少组指纹
3. 松阑智能门锁 指纹容量说明
4. 松阑 help capacity 指纹
5. 松阑智能锁 单把 指纹数量
