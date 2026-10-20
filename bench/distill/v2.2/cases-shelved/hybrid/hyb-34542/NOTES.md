## Traps
TR-TRUNC, TR-MULTISRC

## Reference solution
 一次 web_fetch 同时取 2 个页面（各存入 .web/，各返回开头和 outline）
read_file 按各页 outline 跳到后面的章节共 3 次（或 search_text 在 .web 里搜）
write_file 写入 baggage-compare.md
作答，说明哪个页面更新或更权威。

## Why the answer is unique
Every page contributes facts that sit after its first 1200 tokens; the answer must carry facts from all pages.

## Estimated trajectory tokens
14725
(fixture: skyharbor-air.example/travel/baggage=5050, kestrel-jet.example/help/bags=5275)


## Five alternative phrasings of the task
1. I'm flying either SkyHarbor or Kestrel Jet next month. Use https://skyharbor-air.example/travel/baggage and https://kestrel-jet.example/help/bags to build a baggage comparison in baggage-compare.md: cabin bag, first checked bag fees and bikes.
2. 麻烦帮我：I'm flying either SkyHarbor or Kestrel Jet next month. Use https://skyharbor-air.example/travel/baggage and https://kestrel-jet.example/help/bags to build a baggage comparison in baggage-compare.md: cabin bag, first checked bag fees and bikes.
3. I'm flying either SkyHarbor or Kestrel Jet next month. Use https://skyharbor-air.example/travel/baggage and https://kestrel-jet.example/help/bags to build a baggage comparison in baggage-compare.md: cabin bag, first checked bag fees and bikes. (keep it organised)
4. 想请你看看：I'm flying either SkyHarbor or Kestrel Jet next month. Use https://skyharbor-air.example/travel/baggage and https://kestrel-jet.example/help/bags to build a baggage comparison in baggage-compare.md: cabin bag, first checked bag fees and bikes.
5. 再确认一下：I'm flying either SkyHarbor or Kestrel Jet next month. Use https://skyharbor-air.example/travel/baggage and https://kestrel-jet.example/help/bags to build a baggage comparison in baggage-compare.md: cabin bag, first checked bag fees and bikes.
