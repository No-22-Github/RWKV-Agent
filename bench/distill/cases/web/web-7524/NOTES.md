## Traps
- TR-SNIPPETVAGUE: 官方文档摘要只有「请求格式与字段说明」，没有数字；车队博客摘要带着 50，顺手就答了。

## Reference solution
1. 取题面给出的 https://geo.yantai.example/docs/track。
2. 正文写「单次请求最多上传 20 个轨迹点」，作答 20。

## Why the answer is unique
官方文档是接口行为的权威来源，「最多上传 20 个轨迹点，超出部分请分包发送」是明确约束；博客的 50 是第三方「能出结果」的越限实测，还说出了代价（流量费多三成），不是接口上限。答案唯一。

## 正确答案
20

## Five alternative phrasings
1. 砚台地理 轨迹上传 接口文档
2. 砚台 轨迹 一次多少点
3. 砚台地理 track upload 限制
4. 砚台 轨迹点 上限
5. 砚台地理 批量轨迹 文档
