## Traps
- TR-MULTISRC: the intake file holds the weight into the kiln and the packing file the weight that left, and a loss needs both. The intake file on its own gives 5681.6 kilograms, which is the weight handled rather than the weight lost.
- TR-DUPROW: the intake export was run twice and writes three of the August intakes out again. Adding every intake row instead of every intake answers 3292.5 instead of 2823.4.

## Reference solution
1. List the workspace: the August intake file, the August packing file and a readme.
2. Read README.md: the intake export was run again, so part of the month appears twice.
3. Read kiln_intake_2026-08.csv and packing_records_2026-08.csv; count each intake_id once, add its kg_in and subtract the kg_out total: 2823.4 kilograms.

## Why the answer is unique
The readme states one row per intake and one row per packed consignment, gives kg_in as the weight into the kiln and kg_out as the weight that left, and says the intake export was run again: the repeated rows match their originals in every column, so they are the same intakes written twice and counting each intake_id once is the only reading of the file. The loss is the intake total less the packed total, 2823.4 kilograms.
