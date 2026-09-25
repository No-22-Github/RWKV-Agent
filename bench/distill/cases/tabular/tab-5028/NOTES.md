## Traps
- TR-MULTISRC: the despatch log counts lengths and only timber_volumes.csv carries the volume one length comes
  to, so the log on its own yields a count of 2411 lengths rather than a volume.

## Reference solution
1. List the workspace: the August despatch log, the volume table and a short readme.
2. Read timber_volumes.csv and note the cubic metres per length for each timber code.
3. Read despatch_log_2026-08.csv and keep the Whitcombe Joinery rows.
4. Multiply the lengths on each of those rows by the volume for its timber code and add: 210.5 cubic metres.

## Why the answer is unique
A volume needs both files: the despatch log holds which customer took how many lengths and of which timber code,
while the volume table holds the only figure for how much timber one length of that code is. Neither file alone
gives a volume, so the figure comes from matching the two on timber code and adding the products. The result is
210.5 cubic metres.
