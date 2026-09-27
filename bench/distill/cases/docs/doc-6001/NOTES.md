## Traps
- None. The schedule carries exactly one row per component and the coolant row is the only one naming the cooling circuit, so there is no second figure for a solver to weigh against 60000.

## Reference solution
1. Read README.md: the schedule lists the parts that wear on a fixed mileage cycle.
2. Read maintenance/service-schedule.csv: the Coolant row carries `interval_km` 60000. The answer is 60000.

## Why the answer is unique
The schedule is the complete list of fixed mileage cycles and coolant has exactly one row, so 60000 is the only figure the handbook gives for the cooling circuit. The 15000, 20000, 90000, 120000 and 30000 belong to other components, and the winter checklist adds inspections without touching the coolant cycle. The answer is 60000.
