## Traps
- TR-AMBIG: the first message asks for the September fault count without naming a site. The log carries two sites, so a first turn that reports 6 (both), 4 or 2 has guessed; the correct first turn is a question with no tool call. The second turn names Cobbleworth and the answer is 4. The careless answer is the Pendlebury count 2.

## Reference solution
1. Turn 1: ask which site the board pack covers; no calls.
2. Turn 2 (Cobbleworth named): read faults/fault-log-2026-09.csv and count the Cobbleworth rows. That is 4, a total of 2 calls.

## Why the answer is unique
Four of the six September rows name Cobbleworth, so the clarified request has the single answer 4. The decoy 2 is the Pendlebury count, and the README keeps the two sites on separate reports, so the Pendlebury rows cannot be folded into the Cobbleworth figure. Nothing else in the month is missing: every row carries a site, so no row is unassignable.
