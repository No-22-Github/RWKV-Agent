## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
write_file 写入 commute-cost.md
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14398
(fixture: citybike-share.example/pricing=5058, zipscoot.example/prices=4940)


## Five alternative phrasings of the task
1. I commute 25 minutes each way. Compare CityBike (https://citybike-share.example/pricing) and ZipScoot (https://zipscoot.example/prices) and write commute-cost.md with per-minute prices, monthly pass and the penalty for parking wrong.
2. 麻烦帮我：I commute 25 minutes each way. Compare CityBike (https://citybike-share.example/pricing) and ZipScoot (https://zipscoot.example/prices) and write commute-cost.md with per-minute prices, monthly pass and the penalty for parking wrong.
3. I commute 25 minutes each way. Compare CityBike (https://citybike-share.example/pricing) and ZipScoot (https://zipscoot.example/prices) and write commute-cost.md with per-minute prices, monthly pass and the penalty for parking wrong. (keep it organised)
4. 想请你看看：I commute 25 minutes each way. Compare CityBike (https://citybike-share.example/pricing) and ZipScoot (https://zipscoot.example/prices) and write commute-cost.md with per-minute prices, monthly pass and the penalty for parking wrong.
5. 再确认一下：I commute 25 minutes each way. Compare CityBike (https://citybike-share.example/pricing) and ZipScoot (https://zipscoot.example/prices) and write commute-cost.md with per-minute prices, monthly pass and the penalty for parking wrong.
