## Traps
- TR-MULTISRC: the delivery log weighs the loads and grade_prices.csv holds the only price for each grade, so
  the log alone gives the 424.6 tonnes delivered rather than a value.
- TR-DUPROW: the weighbridge software was reloaded mid-month and 12 loads were written out a second time under
  their original delivery_id, so pricing every line gives 46650.33.

## Reference solution
1. List the workspace: the August delivery log, the grade price list and a short readme.
2. Read README.md and grade_prices.csv: one row per load, and the price of a tonne of each grade.
3. Read deliveries_2026-08.csv and keep the Cawdor Brickworks loads, one line per delivery_id.
4. Multiply each load's tonnes by the price of its grade and add: 33785.92 pounds.

## Why the answer is unique
A value needs a weight and a price, and only the price list carries the price of each grade, so the two files
have to be joined on grade. The reprinted lines repeat their delivery_id and every other field, so they are the
same load written out twice, and the customer named in the request picks out the same set of loads under any
reading. The value is 33785.92 pounds.
