## Traps
- TR-AMBIG: the first message never says which currency the deposit is quoted in and carries no amount, so no figure can be booked from it; the correct first move is to ask and call nothing. On the clarified turn the careless value is 3437.5, obtained by multiplying 2750 by 1.25 instead of dividing.

## Reference solution
1. Turn 1: ask which currency the deposit is in; no tool calls (ref_calls 0).
2. Turn 2 (US dollars named with amount and rate): 2750 / 1.25 = 2200 pounds; no tool calls.

## Why the answer is unique
The clarified message states the rate as 1.25 dollars per pound, so one pound costs 1.25 dollars and pounds = dollars divided by 1.25; 2200 is the only figure the text supports. The decoy 3437.5 multiplies by the rate, which converts pounds into dollars, the direction the message does not ask for, so it is not a reading of the clarified request; no other operation on the two stated quantities answers a pound amount.
