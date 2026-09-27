## Traps
- TR-AMBIG: the first message never says which offsite the quote is for and carries no session counts, so no headcount can be computed from it; the correct first move is to ask and call nothing. On the clarified turn the careless value is 29, the naive sum 18 + 11 that counts the 4 all-day attendees twice.

## Reference solution
1. Turn 1: ask which offsite the catering figure is for; no tool calls (ref_calls 0).
2. Turn 2 (spring offsite named with both counts and the overlap): 18 + 11 - 4 = 25 people; no tool calls.

## Why the answer is unique
The clarified message says 4 of the morning group stayed on for the afternoon, so those 4 are already inside both counts, and it says to count each person once, so the headcount is 18 + 11 - 4 and 25 is the only figure the text supports. The decoy 29 adds the two counts without removing the overlap, which counts the 4 all-day people twice and contradicts the instruction to count each person once, so it is not a reading of the clarified request; no other combination of the three stated numbers answers a once-counted headcount.
