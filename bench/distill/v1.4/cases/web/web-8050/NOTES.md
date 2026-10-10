## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.cyclingnotes.example.org/harbourline）给出 GBP 3  / £3  / GBP 3. / £3.，与官方页不一致；官方页（https://www.harbourline.example/fares/bicycles，2026-09-18）给出 4.50。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://www.harbourline.example/fares/bicycles，读出 4.50。
终答示例：A bicycle costs GBP 4.50 each way from 1 October 2026 (e-bikes GBP 6.00; folding bikes in a bag are free), according to Harbourline's fares page. An older cycling blog's fare is out of date.

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 4.50 才是答案，GBP 3  / £3  / GBP 3. / £3. 是被取代 / 转述错误的值。The ferry operator's fare page announces the October 2026 price; the blog is from 2025.

## Five alternative phrasings of the task
1. Harbourline ferry bicycle fare
2. Harbourline ferry cost to bring a bike
3. Harbourline bikes on board price each way
4. How much is a bike ticket on Harbourline?
5. Harbourline ferries bicycle fares
