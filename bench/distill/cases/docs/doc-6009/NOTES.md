## Traps
- TR-DECOY: the fridge freezer row carries `parts_years` 3 and `labour_years` 4. A solver that reads the first term on the row, or reads the question as "how long is the appliance covered", reports 3 instead of the labour term 4.

## Reference solution
1. Read README.md: each model's row carries separate parts and labour terms in years, and the question is about the work the manufacturer sends out.
2. Read warranty/cover.csv: the Fridge freezer row carries `labour_years` 4; the 3 on the same row is the parts term. The answer is 4.

## Why the answer is unique
The row separates the two terms into named columns, and the question asks about the work the manufacturer sends out, which is the labour column, so 4 is the only reading that matches. The decoy 3 is the parts term on the same row; the dishwasher's 5, the washing machine's 3 and the cooker hood's 2 belong to other models. Reading the parts term as the labour term is the mistake the case is built around. The answer is 4.
