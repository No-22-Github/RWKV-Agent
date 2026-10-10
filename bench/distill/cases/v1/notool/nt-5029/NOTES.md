## Traps
- TR-NOTOOLNEED: the order sheet and the bushel-weight table are in the workspace. Reading the barley row instead of the wheat row turns 84 short tons into 3,500 bushels.

## Reference solution
No steps; ref_calls is 0. 84 short tons x 2,000 lb per ton / 60 lb per wheat bushel. The answer is 2800.

## Why the answer is unique
A short ton is 2,000 lb and the wheat bushel the mill books is 60 lb, so 84 x 2,000 / 60 = 2,800 bushels. 3,500 is the same purchase divided by the 48 lb barley bushel that sits one row below the wheat row; the order line names wheat, and the table keys each bushel weight by commodity, so the wheat row is the only one that applies.
