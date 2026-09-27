## Traps
- TR-DEFN: the question asks for net weight, which README.md defines as gross minus tare, while the most prominent numbers on the three in-window WEIGH-OUT lines are the gross figures. Summing the gross values of the three loads gives 24295; their net total is 17230.

## Reference solution
1. List the workspace: README.md and logs/weighbridge.log.
2. Read README.md: net weight is gross minus tare; ARRIVE lines are not weigh-outs.
3. Read logs/weighbridge.log, take the WEIGH-OUT lines stamped 13:00:00 up to 14:00:00 (13:12, 13:38, 13:51) and total gross minus tare: 6210 + 4760 + 6260 = 17230.

## Why the answer is unique
The README pins net to the difference of the two weights the line carries, so the gross-only sum is not a defensible reading of "net weight". The window cut is on the WEIGH-OUT stamps and the two in-window ARRIVE lines are different events, so the set of loads is fixed at three and each contributes exactly gross minus tare. The answer is 17230.
