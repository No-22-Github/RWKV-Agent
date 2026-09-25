## Traps
- TR-DECOY: the summary line carries the session's cycle count and its gas total but no garment total, and adding the `load` of every cycle gives 929 instead of 518. The threshold has to be applied to each cycle line's `fuel` value so that only the heavier cycles' loads are added.

## Reference solution
1. List the workspace: README.md and logs/boiler.log.
2. Read README.md: `load` is the garments a cycle took in, `fuel` is the gas units it drew, and the summary line carries the session's cycle count and gas total.
3. Read logs/boiler.log. The cycle lines pair fuel with load as load 76 against fuel 76, load 88 against fuel 64, load 63 against fuel 82, load 91 against fuel 69, load 70 against fuel 71, load 84 against fuel 85, load 67 against fuel 66, load 93 against fuel 79, load 72 against fuel 73, load 86 against fuel 68, load 60 against fuel 84, load 79 against fuel 62; the cycles over 70 gas units are the ones that drew 76, 82, 71, 85, 79, 73, 84, and their loads 76, 63, 70, 84, 93, 72, 60 add up to 518.

## Why the answer is unique
The question sets a threshold on the gas a single cycle drew, and README.md says `fuel` is that number while `load` is the garments taken in, so the answer is the loads of the cycles whose own fuel value is over 70. Those loads total 518 garments. The decoy 929 is the whole session's load, which also counts the cycles that stayed under the threshold, and the summary line's gas total is neither a garment count nor a threshold. Testing `fuel` line by line gives 518.

## Fixture notes
The session runs on 16 November 2026 and every cycle line is on that day. The summary line accounts for all 12 cycle lines, so the file can be read as complete.
