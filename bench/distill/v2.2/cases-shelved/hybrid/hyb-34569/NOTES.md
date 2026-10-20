## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 read_file 读预算表；turn2 web_fetch 长页面 -> read_file 跳到价格章节；turn3 算总价；turn4 与第一轮预算比较，差额 600

## Why the answer is unique
The last turn compares the web price total with the budget read in the first turn.

## Estimated trajectory tokens
10176
(fixture: haian-expo.example/venues/halls-pricing=5774)


## Five alternative phrasings of the task
1. 年会筹备预算表在活动文件夹里，报告厅租金一项预算是多少？
2. 麻烦帮我：年会筹备预算表在活动文件夹里，报告厅租金一项预算是多少？
3. 年会筹备预算表在活动文件夹里，报告厅租金一项预算是多少？（用中文回答）
4. 想请你看看：年会筹备预算表在活动文件夹里，报告厅租金一项预算是多少？
5. 再确认一下：年会筹备预算表在活动文件夹里，报告厅租金一项预算是多少？
