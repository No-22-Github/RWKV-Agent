## Traps
- TR-DECOY: the same file holds the south lane's loads and their records look exactly like the north lane's, so taking the heaviest load of the day without reading `lane` gives 29140 instead of 28510.

## Reference solution
1. List the workspace: README.md and logs/weighbridge.jsonl.
2. Read README.md: the bridge serves two lanes and `load_kg` is the weight the bridge recorded.
3. Read logs/weighbridge.jsonl, or filter it to `lane` = north and take the largest `load_kg`: the north records run from 17610 to 28510.

## Why the answer is unique
README.md says the bridge serves two lanes and every record carries the lane it came through, so a south record is not a north load whatever its weight. The north records top out at 28510 kg, recorded at 13:47:29; the decoy 29140 is the heaviest load of the day, which came through the south lane, and the smallest north load answers nothing. With `lane` read, the answer is 28510.

## Fixture notes
Every `load_kg` value is a bare integer and no two records share a weight, so the largest north value is unique. The file covers 20 August 2026 only and `planks` is never needed.
