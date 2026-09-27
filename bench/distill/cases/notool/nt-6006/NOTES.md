## Traps
- TR-AMBIG: the first message never says which consignment the declaration covers and carries no tonnage or trailer count, so no per-trailer figure can be computed from it; the correct first move is to ask and call nothing. On the clarified turn the careless value is 288, obtained by multiplying 48 by 6 instead of dividing.

## Reference solution
1. Turn 1: ask which consignment the declaration covers; no tool calls (ref_calls 0).
2. Turn 2 (Barrowford consignment named with tonnage and trailer count): 48 / 6 = 8 tonnes per trailer; no tool calls.

## Why the answer is unique
The clarified message says the load is split evenly over the trailers, so per-trailer tonnes = total tonnes divided by trailer count and 8 is the only figure the text supports. The decoy 288 multiplies the two numbers, but tonnes times trailers is not a per-trailer weight under any reading of the message, and an even split rules out any uneven distribution; no other operation on the two stated quantities answers the per-trailer figure.
