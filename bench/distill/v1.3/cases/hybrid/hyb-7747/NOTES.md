## Traps
- TR-AMBIG: the request names no month while the log spans late July, August and early September. Summing every defective row gives 580.8, which is not the review figure until the user picks a month.

## Reference solution
1. Turn 1: the month is a required parameter only the user holds; ask which month the review covers (no tool calls).
2. Turn 2: the user answers August 2026.
3. Read logs/refunds.csv, keep reason=defective rows dated 2026-08: 128.50, 76.25, 212.80, 19.95.
4. Total 437.50 and reply with the number alone.

## Why the answer is unique
 The decoy 580.8 folds in the 2026-07-30 and 2026-09-02 defective rows; once the user pins the review to August 2026 those rows are outside the stated scope, so no defensible reading of the clarified request reaches any other total. Turn 1 is judged only on asking for the missing month.

## Five alternative phrasings of the task
1. What did defective refunds cost us this month?
2. Give me the defective-refund total for the review.
3. Add up the defective-item refunds, please.
4. I need the refund value for broken items, one figure.
5. How much did we refund on defective items for the review?
