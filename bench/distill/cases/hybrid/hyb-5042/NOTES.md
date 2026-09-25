## Traps
- TR-AMBIG: the card holds a weekday call-out fee of 48 and a weekend one of 72, and the
  request asks for the call-out fee without saying which column applies. Both are the
  card's own figures, so the assistant has to ask which rate the quote is on.

## Reference solution
1. list_files: the workspace holds rates/callout-card.csv and README.md.
2. read_file rates/callout-card.csv: the callout_fee row carries two figures, so the
   request is not settled and the assistant asks which column applies.
3. Turn 2 settles on the weekend rate: the callout_fee row reads 72 in that column.

## Why the answer is unique
After the clarification the quote is on the weekend column, and the README says the
office picks the column that matches the visit, so the fee is the figure written in the
weekend column of the callout_fee row: 72. The decoy 48 is the same row's weekday figure;
it is the card's own call-out fee, but it belongs to the column the request was settled
against.

## Five alternative phrasings of the task
1. larchmoor heating rate card
2. call-out fee weekday and weekend larchmoor
3. larchmoor heating callout_fee rate
4. larchmoor heating rates for letting agents
5. larchmoor heating hourly rate and callout
