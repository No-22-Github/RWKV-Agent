## Traps
- TR-DEFN: the CSV column order is fixed by the header; existing rows (another city) must stay untouched; low/high are bare numbers, the rain chance keeps its % sign.
- TR-DECOY: today (多云 12~22 15%) is the first row; the row is for tomorrow.
Newline policy: expected = existing text (ends with one newline) + the new row + exactly one trailing newline.

## Reference solution
1. get_weather {"location": "太原", "days": 2}
2. append_file 记录/天气.csv with "2026-09-17,太原,阴,13,21,35%\n" (or write_file with the whole text)
3. read_file 记录/天气.csv to confirm
Final answer: 已在 记录/天气.csv 末尾追加太原明天的一行（阴，13~21，降水概率 35%）。

## Why the answer is unique
明天 is the second forecast row; the column order comes from the header.

## Five alternative phrasings of the task
1. 把太原明天的天气追加进天气.csv
2. 记录/天气.csv 末尾加一行太原 9 月 17 日的预报
3. 天气表补上太原明天那一行
4. 太原明天预报按表头格式记到 csv 里
5. Append Taiyuan's forecast for tomorrow as a new row of the weather CSV.
