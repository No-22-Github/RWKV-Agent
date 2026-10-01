## Traps
- 无陷阱（L0 基题）。同一页三行各对应一个移除版本：9 / 10 / 11，题面问
  /v1/exports，只有 9 一个值与之对应。

## Reference solution
1. 取题面给出的 https://docs.pellwick.example/deprecations 页面（web_fetch）（1）
2. 读 /v1/exports 一行，答案 9（2）

## Why the answer is unique
页面三行分别是 /v1/exports → 9、/v1/snapshots → 10、/v1/segments.bulk → 11，
题面点名 /v1/exports，页面上不存在关于该端点的第二种读法，答案唯一。

## 正确答案
9

## Five alternative phrasings
1. pellwick analytics v1 exports removed version
2. pellwick deprecations exports endpoint
3. which api version removes pellwick exports
4. pellwick analytics api retirement timeline
5. pellwick docs deprecations v1 exports
