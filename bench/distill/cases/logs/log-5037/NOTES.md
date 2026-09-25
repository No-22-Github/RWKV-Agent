## Traps
- TR-DEFN: every run carries two weights. `charged` is the larger, more conspicuous one, the scrap and returns put into the furnace; the question asks for the iron poured out, which is `tapped`. Totalling the charged column gives 893 instead of 817.

## Reference solution
1. List the workspace: README.md and logs/melting-shift.log.
2. Read README.md: `charged` is the tonnes put into the furnace and `tapped` is the tonnes of iron poured out of it, the melt loss being what stayed behind.
3. Read logs/melting-shift.log and total the `tapped` column over the 19 runs: 817 tonnes.

## Why the answer is unique
README.md defines the two columns, and the question asks for the iron the shift poured out, which is the metal that left the furnaces, so `tapped` is the column the reconciliation needs. Every run's `charged` exceeds its `tapped` by the melt loss, so the two totals differ by what was lost in the melt and cannot both be the iron poured. The decoy 893 is the total of the charged column, which includes metal that never left the furnace. With the definition applied, the answer is 817.

## Fixture notes
Both weight columns are plain integers in tonnes, so either can be totalled directly and the choice between them is the whole question. The closing line adds up only the runs and their heats, so the tonnes total has to be built from the run lines, and the melt loss is the same small amount on every run.
