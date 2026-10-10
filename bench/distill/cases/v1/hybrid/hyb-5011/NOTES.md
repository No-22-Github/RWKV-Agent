## Traps
- TR-AMBIG: the first request asks how much cider Ashwell took, and each load is
  recorded both as cases and as bottles. Counting cases gives 348; counting
  bottles gives 4176. The request leaves the unit open, so the assistant has to
  ask before adding anything up.

## Reference solution
1. Turn 1: the loading record holds two measures of the same consignments and
   the request does not pick one, so the assistant asks and calls no tool.
2. list_files: the workspace holds despatch/ashwell-2026-09.csv and README.md.
3. Turn 2 settles it on cases. read_file the despatch file and add the cases
   column: 74 + 98 + 61 + 115 = 348.

## Why the answer is unique
With cases fixed as the unit, each of the four loads contributes its own cases
figure once, and the README confirms the bottle count is the same consignment
expressed the other way rather than a separate delivery. The decoy 4176 is the
bottle column for the same four loads, a real figure that answers the request in
the other unit. Four loads were despatched in September and no load is listed
twice, so the account took 348 cases.

## Five alternative phrasings of the task
1. wrenfield and cole ashwell account september despatch
2. cases and bottles despatched to ashwell in september
3. cider loads sent to the ashwell account
4. wrenfield and cole september despatch summary by load
5. ashwell cider volume counted in cases
