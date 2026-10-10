## Traps
- TR-AMBIG: the stores list holds two bins of M8 bolts, a stainless one with 132 and a
  zinc one with 96, and the request names the item without the finish. Both rows are
  genuine M8 bolt stock, so the assistant has to ask which bin is meant.

## Reference solution
1. list_files: the workspace holds stores/bolt-bins.csv and README.md.
2. read_file stores/bolt-bins.csv: the list carries two M8 bolt rows that differ in
   finish, so the request is not settled and the assistant asks which bin is meant.
3. Turn 2 settles on the stainless bin: its M8 bolt row holds 132.

## Why the answer is unique
After the clarification only the stainless bin is in scope, and the list holds one row
per bin, so the M8 bolt stock wanted is that row's 132. The decoy 96 is the zinc bin's
M8 bolts; it is real stock of the same item, but the README says the finish decides which
bin is meant and the check was settled on the stainless bin.

## Five alternative phrasings of the task
1. oxholme stores bin list
2. m8 bolt stock at oxholme stores
3. oxholme stores stainless and zinc bins
4. oxholme september stock check bolts
5. oxholme stores bolts by finish
