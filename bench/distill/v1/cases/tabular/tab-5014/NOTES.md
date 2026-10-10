## Traps
- TR-DEFN: the sheet's most conspicuous figure is the largest volume drawn, but the request is for the used share
  of capacity, which peaks on a smaller tank. Reporting the rate of the tank with the largest used_litres gives
  50.0 instead of 96.2.

## Reference solution
1. List the workspace: the August usage sheet and a short readme.
2. Read README.md: capacity_litres is the working volume and used_litres the volume drawn during the month.
3. Read tank_usage_2026-08.csv, divide used_litres by capacity_litres for every tank, and take the largest share:
   96.2 percent.

## Why the answer is unique
The readme fixes what each column measures, so a tank's utilisation rate is the quotient of the two columns rather
than either column on its own; ranking by used_litres answers a different question and lands on 50.0. Only one tank
reaches the top share, so 96.2 is the only rate the sheet supports.
