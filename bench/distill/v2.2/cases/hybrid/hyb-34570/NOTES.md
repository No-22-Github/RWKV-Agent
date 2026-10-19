## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 read_file 读预算表；turn2 web_fetch 长页面 -> read_file 跳到价格章节；turn3 算总价；turn4 与第一轮预算比较，差额 18

## Why the answer is unique
The last turn compares the web price total with the budget read in the first turn.

## Estimated trajectory tokens
10120
(fixture: inkwell-press.example/prices/flyers=5841)


## Five alternative phrasings of the task
1. Our print budget is in marketing/spring-campaign-print.csv. How much did we set aside for the A5 flyers per 1000 line?
2. 麻烦帮我：Our print budget is in marketing/spring-campaign-print.csv. How much did we set aside for the A5 flyers per 1000 line?
3. Our print budget is in marketing/spring-campaign-print.csv. How much did we set aside for the A5 flyers per 1000 line? (keep it organised)
4. 想请你看看：Our print budget is in marketing/spring-campaign-print.csv. How much did we set aside for the A5 flyers per 1000 line?
5. 再确认一下：Our print budget is in marketing/spring-campaign-print.csv. How much did we set aside for the A5 flyers per 1000 line?
