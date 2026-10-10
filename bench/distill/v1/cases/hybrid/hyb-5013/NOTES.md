## Traps
- TR-AMBIG: the first request asks how much is still outstanding and the order
  holds both quantities and prices, so "how much" can be read as units or as
  money. Counting units gives 120 + 0 + 2 + 0 = 122; valuing them at the held
  prices gives 223.20 + 145.00 = 368.20. The request does not say which is meant,
  so the assistant has to ask.

## Reference solution
1. Turn 1: "how much" is open between the quantity measure and the money measure
   the file supports, so the assistant asks and calls no tool.
2. list_files: the workspace holds orders/hesketh-order.csv and README.md.
3. Turn 2 settles it on units. read_file the order and subtract per line:
   (480 - 360) + (120 - 120) + (6 - 4) + (60 - 60) = 120 + 0 + 2 + 0 = 122.

## Why the answer is unique
Once the measure is fixed, each line contributes exactly the gap between the two
quantities the file holds for it, and the README states that deliveries are
booked in against the line, so a delivered figure is a reduction of the ordered
figure rather than a separate order. Two lines are fully delivered and
contribute nothing. The decoy 368.20 is the same outstanding quantity priced at
the held unit prices, which answers the request in money. Outstanding on the
Hesketh order: 122 units.

## Five alternative phrasings of the task
1. ellerbeck builders merchants hesketh order outstanding
2. units still to be delivered on the hesketh order
3. order sheet with ordered delivered and unit price columns
4. how much is left on the hesketh order in units
5. outstanding quantities for concrete blocks kerbs sand and cement
