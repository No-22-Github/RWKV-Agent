## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
turn1 read_file 读预算表；turn2 web_fetch 长页面 -> read_file 跳到价格章节；turn3 算总价；turn4 与第一轮预算比较，差额 412

## Why the answer is unique
The last turn compares the web price total with the budget read in the first turn.

## Estimated trajectory tokens
10209
(fixture: anshun-office.example/catalog/monitors=5750)


## Five alternative phrasings of the task
1. 行政那边有个办公设备采购预算表，在行政文件夹里，27 英寸显示器那行预算是多少？
2. 麻烦帮我：行政那边有个办公设备采购预算表，在行政文件夹里，27 英寸显示器那行预算是多少？
3. 行政那边有个办公设备采购预算表，在行政文件夹里，27 英寸显示器那行预算是多少？（用中文回答）
4. 想请你看看：行政那边有个办公设备采购预算表，在行政文件夹里，27 英寸显示器那行预算是多少？
5. 再确认一下：行政那边有个办公设备采购预算表，在行政文件夹里，27 英寸显示器那行预算是多少？
