## Traps
- TR-DECOY: round-sheets/round-15.txt is the next round's sheet, typed the morning after from the sheet that was filed twice, so it reads like the same document: same burner, same shape of line, a setting and a drawing figure a little higher. A solver who picks the similar-looking sheet instead of comparing the sheets reports 1157, which is the wrong figure. The two files that carry the same round word for word are round-sheets/round-14-burner.txt and round-sheets/round-14-works.txt, and both read 1096 bricks.

## Reference solution
1. list_files (1): README.md and three sheets under round-sheets/, round-14-burner.txt, round-14-works.txt and round-15.txt.
2. read_file round-sheets/round-14-burner.txt (2): kiln round sheet 14, setting 1120 greens, drawn 1096 bricks.
3. read_file round-sheets/round-14-works.txt (3): the same sheet word for word, 1096 bricks, so these two are the round written up twice.
4. read_file round-sheets/round-15.txt (4): the next round, drawn 1157 bricks, a different sheet and not part of the pair.

## Why the answer is unique
The question asks for the round that was written up twice, and that is settled by comparing the sheets with each other, not by which one reads most like a kiln sheet. Exactly two files in the folder hold the same words, the burner's copy and the office copy of round 14, and both of them read 1096 bricks on their own drawn line. The round 15 sheet differs from both: its setting is higher, its drawn line reads 1157 and its clamp was sealed at a different minute, so it is not a copy of the pair and 1157 is not the figure of the doubled round. The answer is 1096.
