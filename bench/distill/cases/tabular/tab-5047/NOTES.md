## Traps
- TR-RULEFILE: the rate and the clause for heavy loads both live in intake_terms.md: 3.20 pounds a tonne, and a load over 28 tonnes charged at half the rate on the whole load. The October file holds the tonnages only. Two of the Dunragit Farms loads are over 28 tonnes, so a reader who applies the flat rate to every load answers 1099.84 instead of 1000.8.

## Reference solution
1. List the workspace: the October intake file, the intake terms and a short readme.
2. Read intake_terms.md: the rate is 3.20 pounds a tonne, and a load of more than 28 tonnes is charged at half the rate on the whole load.
3. Read beet_intake_2026-10.csv, keep the Dunragit Farms loads, charge each load at the rate its weight earns and add: 1000.8 pounds.

## Why the answer is unique
The tonnages come from the October file and the rate and the heavy-load clause from the intake terms; nothing else in the workspace states a charge. The clause is written on the whole load, so each load has one rate: half rate above 28 tonnes and the standard rate at or below it. Two of the Dunragit Farms loads are heavier than 28 tonnes and the rest are lighter, so the charge is fixed by the file and the terms and comes to 1000.8 pounds.
