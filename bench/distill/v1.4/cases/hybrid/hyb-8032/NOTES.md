## Traps
- TR-WEBSTALE: 搜索结果里的二手页（https://www.smarthomereview.example.com/alder-hub-2）给出 ，与官方页不一致；官方页（https://alder.example/hub/pricing，2026-08-30）给出 89。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 https://alder.example/hub/pricing，读出 89。同时读本地文件取得对象信息（文件第一行就是决定对象的那一行）。
终答示例：The inventory shows we stock the Alder Hub 2, whose RRP is EUR 89 (incl. VAT) from 1 September 2026 per Alder's price page. The February review's price is the old one.

## Changelog
- v2：S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 89 才是答案， 是被取代 / 转述错误的值。The CSV names the model; Alder's price page lists RRP by model with an effective date.

## Five alternative phrasings of the task
1. Alder's current RRP for the hub model in shop/stock-note.txt
2. What does Alder say the RRP is for the Hub model we stock (shop/stock-note.txt)?
3. Find our Alder Hub model in shop/stock-note.txt and its current recommended price
4. Current Alder recommended retail price for the model in our stock note
5. Alder Hub model we stock: what is its official RRP now?
