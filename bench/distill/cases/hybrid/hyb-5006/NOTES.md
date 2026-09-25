## Traps
- TR-AMBIG: the first request names "the Ridgeway block" while the picking file
  holds two Ridgeway blocks, Ridgeway North and Ridgeway South. Answering from
  Ridgeway North gives 376 (142 + 171 + 63); the block the request was cleared
  for, Ridgeway South, gives 298 (118 + 96 + 84). The file alone cannot say which
  block the request meant, so the assistant has to ask before computing.

## Reference solution
1. Turn 1: the request names a block that the picking file holds twice, so the
   assistant asks which Ridgeway block is meant and calls no tool.
2. list_files: the workspace holds picks/september-2026.csv and README.md.
3. Turn 2 fixes Ridgeway South. read_file picks/september-2026.csv and add that
   block's rows: 118 + 96 + 84 = 298.

## Why the answer is unique
After the clarification only one block is in scope. The file records each day's
pick as its own row under one block name, and no row is repeated, so Ridgeway
South's September crates are its three rows: 118 on 6 September, 96 on 9
September and 84 on 19 September, giving 298. The decoy 376 is the North block's
three rows; it is a real figure, but it answers a different block, and the
request was settled on the South block before the sum was taken.

## Five alternative phrasings of the task
1. cobbleworth vineyard ridgeway block crates september 2026
2. how many crates the ridgeway south block picked in september
3. vineyard picking rows for ridgeway north and ridgeway south
4. cobbleworth september picking totals by block
5. ridgeway block fruit crates sent to the winery
