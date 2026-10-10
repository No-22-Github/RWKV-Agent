## Traps
- TR-AMBIG: the first request asks how many deliveries the round made, and every
  row counts two different things: the loads the van went out with and the stops
  it made. Counting stops gives 253; counting loads gives 19. The request does
  not say which of the two it means, so the assistant has to ask.

## Reference solution
1. Turn 1: the row counts two different events and the request does not settle
   which one, so the assistant asks and calls no tool.
2. list_files: the workspace holds rounds/september-2026.csv and README.md.
3. Turn 2 settles it on stops. read_file the round file and add the drops column:
   41 + 38 + 29 + 52 + 49 + 44 = 253.

## Why the answer is unique
With stops fixed as the basis, the file gives one drops figure per working day
and the README confirms what the column counts, so each day contributes once and
no day is missing from the six rows. The decoy 19 is the same six rows counted as
loads, which is a real figure in the other column and answers a different
question. Delivery stops across the September round come to 253.

## Five alternative phrasings of the task
1. cawston dairy september round deliveries loads and drops
2. number of stops made on the september milk round
3. daily round sheet with loads and drops for september
4. cawston dairy delivery figures for the new contract
5. september milk round stops by day north and south
