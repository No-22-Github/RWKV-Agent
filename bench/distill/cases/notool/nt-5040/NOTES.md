## Traps
- TR-NOTOOLNEED: the rota sheet and the offset table are in the workspace, and both stations keep one offset all year. Reading the Phoenix offset as the Bogota five hours gives a 360 minute lead.

## Reference solution
No steps; ref_calls is 0. Lagos is +60 minutes and Phoenix is -420 minutes; the lead is 480. The answer is 480.

## Why the answer is unique
Lagos runs at UTC+01:00 and Phoenix at UTC-07:00, so the Lagos clock is 60 minus -420 = 480 minutes ahead. 360 is what the five hour Bogota row would give; the desk sheet names Phoenix and Lagos, and the table keys -07:00 to Phoenix and +01:00 to Lagos, so the third row belongs to neither desk. The sign matters: subtracting the two offsets without it would put Lagos behind.
