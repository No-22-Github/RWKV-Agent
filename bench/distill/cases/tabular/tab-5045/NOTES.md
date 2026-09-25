## Traps
- TR-DECOY: hide_intake_2026.csv holds the light line beside the main line, and the calfskin batches are the bigger ones: the largest calfskin batch holds 804 pieces, more than any cowhide batch. That batch is the most conspicuous figure in the log, so a reader who takes the largest batch of the file answers 804 instead of 412.

## Reference solution
1. List the workspace: the intake file and a short readme.
2. Read hide_intake_2026.csv and note that hide_type separates the cowhide batches from the calfskin batches.
3. Take the largest pieces value among the Cowhide rows: 412 pieces.

## Why the answer is unique
The question asks for a cowhide batch, and the readme says the batch line is recorded in hide_type, so the calfskin batches are a different line of intake and cannot supply the figure even when they are larger. Within the cowhide rows one value is the largest and it occurs once, so the answer is 412 pieces.
