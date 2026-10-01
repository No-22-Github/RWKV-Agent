## Traps
- TR-AMBIG: the request filters invoices by a threshold that appears nowhere in the workspace; the user alone holds it. Summing all six August lines gives 7867.4, which ignores the filter the committee applies.

## Reference solution
1. Turn 1: the threshold is a required parameter absent from both prompt and workspace; ask for it (no tool calls).
2. Turn 2: the user sets the threshold at 1,300 USD.
3. Read logs/freight-invoices.csv, keep August lines above 1300: 1840.00, 1592.75, 1420.00.
4. Total 4852.75 and reply with the number alone.

## Why the answer is unique
 The decoy 7867.4 is the unfiltered August total; the clarified request sums only lines above 1300, and 1265.50, 640.25 and 1108.90 fall below it. Whether a line sits above or below the threshold is settled once the user states it, so no second reading survives.

## Five alternative phrasings of the task
1. Add up the August freight invoices over our review cutoff.
2. What is the total of the big August freight lines?
3. Sum the August freight spend that clears the committee threshold.
4. Give me the August freight total above the review line.
5. Total the costly August freight invoices for the committee.
