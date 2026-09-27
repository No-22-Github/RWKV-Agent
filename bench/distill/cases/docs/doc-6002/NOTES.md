## Traps
- TR-ABSENT: the schedule has no row for brake fluid. The nearest row is `Brake pads` at 30000, and a solver that takes the brake-related row's interval as the fluid's cycle reports 30000 instead of UNKNOWN.

## Reference solution
1. Read README.md: the schedule lists the parts that wear on a fixed mileage cycle, and a part with no row has no fixed interval.
2. Read maintenance/service-schedule.csv: the rows cover oil, cabin filter, coolant, gearbox oil, air dryer and brake pads; brake fluid is not among them.
3. Read docs/winter-checklist.md: brake fluid is tested for moisture at depot visits, with no mileage cycle. The answer is UNKNOWN.

## Why the answer is unique
The schedule is the complete list of fixed intervals and the README states that a part without a row has none, so a brake fluid cycle does not exist anywhere in the folder. The decoy 30000 is the brake pads' interval, a different part of the same system; reading one brake item's cycle as the other's is the mistake the case is built around. The answer is UNKNOWN.
