## Traps
- TR-NEARNAME: three near-named services write this journal. The step-up authentication service is hollingworth-pay-3ds; hollingworth-pay (card authorisations) alone logs 46 ERROR lines in the same window, so counting hollingworth-pay, or blending the three writers, gives 46 or worse. The shared hollingworth-pay prefix is the trap.

## Reference solution
1. Read README.md: the three writer services and that the service field is the third token.
2. Sample the journal head with a line window: line grammar and the CLOSE record.
3. Restrict to the 14:05:00-14:20:00 UTC window (all stamps are UTC) and the ERROR level.
4. Keep only lines whose service field is exactly hollingworth-pay-3ds.
5. Count them: 71.

## Why the answer is unique
The window bounds are stated in the prompt and every stamp is UTC, so the only reading that changes the count is which service counts. README.md maps "step-up authentication service" to exactly one of the three writer names, hollingworth-pay-3ds, and each line belongs only to the service named in it, so lines from hollingworth-pay or hollingworth-ledger are excluded by the record grammar, not by judgement. No event sits on the window boundaries, so inclusive and exclusive readings agree. The count is 71.
