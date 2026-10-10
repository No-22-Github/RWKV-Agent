## Traps
- TR-DECOY: the journal covers three days and the same turbines are curtailed at the same clock hours on each of them, so counting T-7's curtailments on 23 September without the window gives 7 instead of 4, and counting the 12:00-18:00 T-7 curtailments of all three days gives 8.

## Reference solution
1. List the workspace: README.md and logs/curtailment.log.
2. Read README.md: the journal covers three days, CURTAIL marks an instruction to hold a turbine back, and the closing line accounts for every instruction line.
3. Read logs/curtailment.log. The T-7 curtailments on 23 September inside 12:00-18:00 are at 12:19:44, 14:08:37, 16:03:21 and 17:29:33, so 4 of them.

## Why the answer is unique
The question fixes a turbine, a day and a window, and every instruction line carries all three, so the count is read off the lines that match on each. Four lines do: the two neighbouring days' instructions and the 23 September curtailments outside the window are other instructions. The decoy 7 is the whole of 23 September rather than the window, and 8 is the window taken across all three days. With all three conditions applied, the answer is 4.

## Fixture notes
All stamps are UTC and the closing line accounts for all 18 instruction lines. T-7 is both curtailed and released in the journal, so the two event kinds are both present for it.
