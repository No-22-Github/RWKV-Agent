## Traps
- TR-DECOY: both furnaces draw the same batches through the same shift, so the F-1 runs look like the ones the question asks for. The closing line also prints the shift's heat total of 108, which is the number a reader reaches for when the two furnaces are not separated; F-2 alone fired 66 heats.

## Reference solution
1. List the workspace: README.md and logs/melting-shift.log.
2. Read README.md: one line per run, `furnace` names which of the two furnaces ran it and `heats` is how many times that run fired it.
3. Read logs/melting-shift.log and total `heats` over the runs whose furnace is F-2: 7+9+8+6+9+7+8+6+6 = 66.

## Why the answer is unique
README.md says the foundry runs two furnaces and each run names the one it belongs to, so the F-1 runs are the other furnace's work and cannot be counted as F-2 heats. The eight F-2 runs fired 66 heats between them. The decoy 108 is the shift's total heats, printed on the closing line, which is what the two furnaces fired together, and totalling the tonnes column answers a weight question rather than this one. With the furnace applied, the answer is 66.

## Fixture notes
Every line carries a UTC stamp on 17 September 2026 and the closing line makes the file self-checking over both its counts. The two furnaces alternate through the shift, so neither can be read off one half of the file, and the F-2 heats are spread rather than grouped.
