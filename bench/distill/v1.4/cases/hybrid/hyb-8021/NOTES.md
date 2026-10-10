## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.dayin-luntan.cn/t/maple-p40）给出 12 个月 / 12个月 / 保修一年 / 保修 1 年，与官方页不一致；官方页（https://www.maple-print.cn/support/warranty，2026-05-06）给出 24。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.maple-print.cn/support/warranty，读出 24。同时读本地文件取得对象信息（文件第一行就是决定对象的那一行）。
终答示例：采购清单里的是 Maple P40（办公室 2 楼），官方保修政策页写 P40 整机保修 24 个月，也就是两年；论坛帖的说法不是官方口径。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 24 才是答案，12 个月 / 12个月 / 保修一年 / 保修 1 年 是被取代 / 转述错误的值。清单决定型号 P40，官方保修表按型号给期限；论坛帖未区分型号。

## Five alternative phrasings of the task
1. 设备清单里的打印机，Maple 官网写的整机保修多长？
2. 我们买的那台 Maple 打印机，官方保修几个月？
3. 看下采购清单里 Maple 打印机的型号，再查官方保修期
4. 采购清单上的 Maple 打印机整机保修期是多久（以厂商说法为准）
5. Maple 打印机（清单里那台）保修多久
