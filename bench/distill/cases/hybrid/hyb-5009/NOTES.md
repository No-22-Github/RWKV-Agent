## Traps
- TR-AMBIG: the first request names "the September run" while the gas log holds
  two September runs, Sept-A and Sept-B, each spread over two firings. Sept-A
  cost 2768.95 in gas and Sept-B cost 3152.35. The log cannot say which run the
  return means, so the assistant has to ask before adding either set of rows.

## Reference solution
1. Turn 1: two September runs are named in the log and the request does not say
   which one the return covers, so the assistant asks and calls no tool.
2. list_files: the workspace holds runs/kiln-gas-2026.csv and README.md.
3. Turn 2 settles it as Sept-B. read_file the log and add that run's two rows:
   2418.90 + 733.45 = 3152.35.

## Why the answer is unique
Once the run is fixed, the log gives exactly two rows for it and the README
states that a run is charged the gas metered to its kiln between its own start
and end dates, so both Sept-B firings belong to the run and neither row belongs
to the other run. The decoy 2768.95 is the true gas cost of the Sept-A firings,
a different run. No row covers two runs and no firing appears twice, so the
September cost of the run that was settled on is 3152.35.

## Five alternative phrasings of the task
1. barrowby brickworks kiln gas log september runs
2. gas cost of the sept-b kiln run
3. kiln firings and metered gas for september 2026
4. barrowby brickworks energy return gas figures
5. sept-a and sept-b kiln runs gas charges
