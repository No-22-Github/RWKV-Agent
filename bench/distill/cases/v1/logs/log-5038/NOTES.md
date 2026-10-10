## Traps
- TR-DECOY: the journal covers the whole day and the storm pump ran 21 times over it, so the runs outside the window look like the ones the question asks for. Reading the day's storm runs instead of the five hours gives 21 instead of 13. The duty pump also ran twice inside the window, so a reader who takes every run of those hours counts 15.

## Reference solution
1. List the workspace: README.md and logs/storm-pump.log.
2. Read README.md: the station has a duty pump for the ordinary flow and a storm pump cut in when the level rises, `pump` names which one ran, `minutes` is the length of the run and `level` is the sump level it started at.
3. Read logs/storm-pump.log and count the storm runs stamped between 01:00 and 06:00 on 6 September 2026: 01:07, 01:34, 02:02, 02:28, 02:55, 03:11, 03:39, 04:04, 04:33, 05:02, 05:26, 05:41 and 05:58, which is 13 runs.

## Why the answer is unique
README.md says the two pumps are distinct and the closing line reports 21 storm runs and 8 duty runs for the day, so the storm runs are separable from the duty runs and the window is separable from the rest of the day. Thirteen storm runs fall between 01:00 and 06:00. The decoy 21 is the storm pump's whole day, which is what a reader gets by leaving the window out, and 15 is what the window holds when the two duty runs inside it are counted with the storm ones. With both the pump and the window applied, the answer is 13.

## Fixture notes
Every line carries a UTC stamp on 6 September 2026 and the closing line makes the file self-checking over the day. No run is stamped exactly on a window edge, so the count does not turn on whether the edges are included, and the duty pump's runs are interleaved with the storm pump's through the day.
