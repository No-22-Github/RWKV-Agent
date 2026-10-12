## Traps
- Turn 1: exact answer 220; the loose reading (dry-run markers counted, so the second open is the first real window) gives 146.
- Turn 2: exact answer 25; the loose reading (dry-run markers counted and level prefix match) gives 21.
- TR-TRUNC: the file is 46KB and 1227 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk '$2=="MARK" && $4=="WINDOW-OPEN" {k++; if (k==2) on=1; next} $2=="MARK" && $4=="WINDOW-CLOSE" {on=0} on {c++} END{print c+0}' maint/events.txt` -> 220
Turn 2: bash: `awk '$2=="MARK" && $4=="WINDOW-OPEN" {k++; if (k==2) on=1; next} $2=="MARK" && $4=="WINDOW-CLOSE" {on=0} on && $2=="ERR" {c++} END{print c+0}' maint/events.txt` -> 25
Final answer: 25 ERR lines fall inside the second window.

## Why the answer is unique
Windows are delimited by exact marker rows and the second real window is unambiguous once the dry run is excluded. The README (maint/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Number of ERR-level lines in the second maintenance window.
2. Between the second open and its close, count rows whose level is exactly ERR.
3. How many ERR events happened during the second real window?
4. In the second window of events.txt, how many lines are ERR (not ERR-RETRY)?
5. Count the ERR lines inside the window that starts at the second WINDOW-OPEN.
