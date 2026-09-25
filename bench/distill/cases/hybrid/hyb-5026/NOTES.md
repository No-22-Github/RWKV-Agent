## Traps
- TR-AMBIG: the first request names Batch 12, and both mills ran one in September.
  Ashwater's despatches are 60 x 25, 38 x 20 and 55 x 25, giving 3635 kilograms; Cotham's
  are 44 x 20, 41 x 25 and 36 x 15, giving 2445. The despatch file cannot say which mill's
  batch the return covers, so the assistant has to ask.

## Reference solution
1. list_files: the workspace holds despatch/september-2026.csv and README.md.
2. read_file despatch/september-2026.csv: the batch column carries Batch 12 under two
   mills, so the request is not yet settled and the assistant asks which mill is meant.
3. Turn 2 fixes the Ashwater batch. Multiply and add its three despatches:
   60 x 25 + 38 x 20 + 55 x 25 = 1500 + 760 + 1375 = 3635.

## Why the answer is unique
After the clarification one mill's batch is in scope. The README says each row carries the
number of bags and the weight of one bag, so a despatch weighs bags times bag weight, and
the Ashwater rows give 3635 kilograms. The decoy 2445 is Cotham's Batch 12, a real total
for the other mill, and the return was settled on Ashwater before the rows were totalled.
Batch 7 rows carry a different batch name and cannot answer the request.

## Five alternative phrasings of the task
1. ashwater feed mill batch 12 despatch september
2. kilograms of feed in batch 12
3. ashwater and cotham batch 12 despatch totals
4. batch 12 bags and bag weights september
5. feed mill batch 12 output in kilograms
