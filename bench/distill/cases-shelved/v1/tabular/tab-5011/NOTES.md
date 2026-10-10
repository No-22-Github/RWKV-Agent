## Traps
- TR-RULEFILE: the per-kilometre rates and the shuttle rate live in reimbursement_terms.md, not in the trip log.
  Charging every kilometre of every trip at the standard rate gives 1329.84.
- TR-DUPROW: four trip rows are written twice by the export. Settling those rows a second time gives 1349.79.

## Reference solution
1. List the workspace: the quarterly trip log and the co-op's expense terms.
2. Read reimbursement_terms.md for the three rates, and note that one row stands for one completed trip.
3. Read trips_2026-q2.csv, keep one row per trip_id, then settle each trip: the six R-7 shuttle trips at 25.00
   each, the electric van trips at 0.38 per kilometre and the remaining trips at 0.62 per kilometre.
4. Add the settled amounts: 1225.55.

## Why the answer is unique
The terms file fixes all three rates and states that one row is one trip, so the six shuttle trips cannot also be
charged per kilometre and the reprinted rows cannot be settled twice. Applying each rate to the distance on its
row and summing over the 55 distinct trip identifiers leaves exactly 1225.55.
