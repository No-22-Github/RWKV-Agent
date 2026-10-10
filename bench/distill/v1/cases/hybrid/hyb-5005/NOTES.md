## Traps
None. The record is written by the traffic desk alone, carries one cover figure
and one package count, and no second record for this consignment exists.

## Reference solution
1. list_files: the workspace holds dispatch/consignment-4471.json and README.md.
2. read_file dispatch/consignment-4471.json: the record for consignment 4471
   carries insured_value_gbp 4825, which the README names as the cover value the
   desk declared to the carrier.

## Why the answer is unique
The workspace holds one consignment record and its cover field is the only value
of its kind in the file: packages, the collection date and the consignment number
answer different questions and none of them is a cover figure. The README fixes
what the field means (the figure declared to the carrier at collection, printed
on the delivery note), so the number in that field is the answer to the broker's
question and there is no second figure in the workspace that could be meant.
The declared cover value is 4825.

## Five alternative phrasings of the task
1. fenwick forwarding consignment 4471 cover value
2. declared carrier cover for consignment 4471
3. what value did the traffic desk declare to the carrier
4. fenwick forwarding collection record rookhope haulage 4471
5. cover figure printed on delivery note dn-4471
