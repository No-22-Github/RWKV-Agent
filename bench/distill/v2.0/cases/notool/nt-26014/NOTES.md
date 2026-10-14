## Traps
- TR-AMBIG: the first message never says which sessions the reach figure covers and carries no viewer counts, so no distinct-viewer figure can be computed from it; the correct first move is to ask and call nothing. On the clarified turn the careless value is 420, the naive sum 240 + 180 that counts the 75 rerun viewers twice.

## Reference solution
1. Turn 1: ask which sessions the reach figure covers; no tool calls (ref_calls 0).
2. Turn 2 (September session pair named with both counts and the overlap): 240 + 180 - 75 = 345 distinct viewers; no tool calls.

## Why the answer is unique
The clarified message says 75 of the morning viewers caught the rerun as well, so those 75 are already inside both counts, and it says to count each viewer once, so the distinct total is 240 + 180 - 75 and 345 is the only figure the text supports. The decoy 420 adds the two counts without removing the overlap, which counts the 75 twice and contradicts the instruction to count each viewer once, so it is not a reading of the clarified request; no other combination of the three stated numbers answers a once-counted viewer total.
