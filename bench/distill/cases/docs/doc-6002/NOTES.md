## Traps
- TR-ABSENT: the schedule has no row for brake fluid. The nearest row is `Brake pads` at 30000, and a solver that takes the brake-related row's interval as the fluid's cycle reports 30000 instead of UNKNOWN.

## Reference solution
1. Read README.md, maintenance/service-schedule.csv and docs/winter-checklist.md.
2. The schedule's rows cover engine oil, cabin filter, coolant, gearbox oil, air dryer and brake pads, and no brake fluid row exists among them; README.md states a part with no row in the schedule has no fixed interval, and the winter checklist only tests brake fluid for moisture at depot visits, with no mileage figure. No brake fluid flush cycle exists in the folder.
3. Final answer in two or three sentences: name the files checked, say the schedule has no brake fluid row and so no mileage cycle for one, and point to the nearest brake row (the pads) as a different part without quoting its interval. Scored with output_contains_any over "brake fluid", "brake-fluid" or "brake fluid flush"; output_excludes rules out UNKNOWN and the 30000 brake-pads interval, so the reply names the missing cycle instead of quoting any mileage.

## Why the answer is unique
The schedule is the complete list of fixed intervals and README.md states that a part without a row has none, so a brake fluid cycle does not exist anywhere in the folder. The decoy 30000 is the brake pads' interval, a different part of the same system; reading one brake item's cycle as the other's is the mistake the case is built around. The only truthful reply reports the absence: the schedule, README.md and the winter checklist were checked, no brake fluid row exists in the schedule, and the nearest brake row is a different part whose interval is not the answer to the question.
