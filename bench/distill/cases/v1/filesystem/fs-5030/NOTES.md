## Traps
- TR-DUPROW: the sheet filed twice carries the 09:05 Westgate Farm load on two consecutive lines, pasted in twice by the typist. Nothing else separates the two lines, so counting lines instead of loads gives 9, which is the wrong answer; the sheet covers 8 loads.
- TR-DECOY: intake/intake-0902.txt is the next intake day's sheet, typed from the same template with the same three suppliers and the same shape of line. A solver who works from that sheet instead of the one filed twice reports 6.

## Reference solution
1. list_files (1): README.md and three sheets under intake/, intake-0826-mill.txt, intake-0826-office.txt and intake-0902.txt.
2. read_file intake/intake-0826-mill.txt (2): nine load lines, but the 09:05 Westgate Farm barley 16.9 tonnes line appears on two consecutive lines, so the day covered 8 loads.
3. read_file intake/intake-0826-office.txt (3): the same sheet word for word, which confirms these two are the day filed twice.
4. read_file intake/intake-0902.txt (4): the next intake day, six loads, a different sheet and not the one filed twice.

## Why the answer is unique
The sheet filed twice is settled by comparing files, not by which sheet reads most like an intake sheet: the mill copy and the office copy of 26 August carry the same words, and no other pair does. On those two lines the repeated entry matches its twin in time, supplier, grain and weight, down to the minute on the weighbridge, so it is one lorry weighed once and typed in twice, and the day covered 8 loads. Counting 9 treats that single load as two, which asks the reader to believe two lorries from the same farm were weighed in the same minute carrying the same grain at the same weight. The 2 September sheet covers six loads of its own and is a different day's intake, so 6 is not the count of the doubled sheet. The answer is 8.
