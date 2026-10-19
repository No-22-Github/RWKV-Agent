## Traps
TR-TRUNC

## Reference solution
 web_fetch（长页面存入 .web/，只返回开头和 outline）
read_file 按 outline 跳到后面的章节 2 次（或 search_text 在 .web 里搜关键词）
作答。
第二轮追问同一页面的细节：search_text 在 .web 里搜或 read_file 跳读，再作答。

## Why the answer is unique
Facts are spread over several sections; at least two sit after the first 1200 tokens of the page.

## Estimated trajectory tokens
12570
(fixture: ludao-metro.example/news/line-6-opening-plan=6120)


## Five alternative phrasings of the task
1. 鹭岛地铁 6 号线要开通了，运营方案公示在 https://ludao-metro.example/news/line-6-opening-plan 。帮我总结一下线路规模、发车时间、票价优惠和换乘安排。
2. 麻烦帮我：鹭岛地铁 6 号线要开通了，运营方案公示在 https://ludao-metro.example/news/line-6-opening-plan 。帮我总结一下线路规模、发车时间、票价优惠和换乘安排。
3. 鹭岛地铁 6 号线要开通了，运营方案公示在 https://ludao-metro.example/news/line-6-opening-plan 。帮我总结一下线路规模、发车时间、票价优惠和换乘安排。（用中文回答）
4. 想请你看看：鹭岛地铁 6 号线要开通了，运营方案公示在 https://ludao-metro.example/news/line-6-opening-plan 。帮我总结一下线路规模、发车时间、票价优惠和换乘安排。
5. 再确认一下：鹭岛地铁 6 号线要开通了，运营方案公示在 https://ludao-metro.example/news/line-6-opening-plan 。帮我总结一下线路规模、发车时间、票价优惠和换乘安排。
