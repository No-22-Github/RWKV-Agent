## Traps
- TR-AMBIG: the first message never says which fair the attendance figure covers and carries no daily counts, so no attendance figure can be computed from it; the correct first move is to ask and call nothing. On the clarified turn the careless value is 184, the naive sum 96 + 88 that counts the 31 returning visitors twice.

## Reference solution
1. Turn 1: ask which fair the attendance figure covers; no tool calls (ref_calls 0).
2. Turn 2 (Rossdale fair named with both daily counts and the overlap): 96 + 88 - 31 = 153 visitors; no tool calls.

## Why the answer is unique
The clarified message says 31 of the day-one visitors returned on day two, so those 31 are already inside both badge counts, and it says to count each visitor once, so the attendance figure is 96 + 88 - 31 and 153 is the only figure the text supports. The decoy 184 adds the two counts without removing the overlap, which counts the 31 returners twice and contradicts the instruction to count each visitor once, so it is not a reading of the clarified request; no other combination of the three stated numbers answers a once-counted attendance figure.
