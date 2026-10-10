## Traps
- TR-DUPROW: the collector re-sent 5 overheat-alarm ERROR lines unchanged, so the journal holds 19 such lines over 14 batches; counting lines answers 19.
- TR-DECOY: 6 WARN lines say 'kiln overheat margin low', a lesser condition in the same wording family; folding them in answers 20.

## Reference solution
1. Read README.md: line grammar, the re-send rule, and the alarm wording that defines the ERROR.
2. Search 'kiln overheat alarm' and read the line windows around the hits.
3. Keep only ERROR lines, collect batch ids, merge identical re-sends.
4. The distinct count is 14.

## Why the answer is unique
Re-sent lines repeat every field, so the README's re-send rule makes them one batch; the margin WARNs are WARN level and their message opens differently, so neither folds into the ERROR count. The distinct count is 14.
