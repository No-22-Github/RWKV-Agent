## Traps
- TR-AMBIG: the first request names T-14, and the workspace holds two logs for a vehicle
  with that fleet number, one under trips/kemsley and one under trips/rothwell. The
  Kemsley log sums to 800 (178 + 265 + 149 + 208); the Rothwell log sums to 792
  (214 + 186 + 240 + 152). Nothing in either log says which vehicle the claim is for, so
  the assistant has to ask.

## Reference solution
1. list_files: the workspace holds two vehicle logs, one under trips/kemsley and one
   under trips/rothwell, plus README.md.
2. read_file each log: both are named for the fleet number T-14, so the request is not
   yet settled and the assistant asks which vehicle is meant.
3. Turn 2 fixes the Kemsley vehicle. Add its rows: 178 + 265 + 149 + 208 = 800.

## Why the answer is unique
After the clarification only the Kemsley log is in scope. Each log holds one row per trip
under the depot the vehicle works from, and the README states that two depots each run a
T-14, so the fleet number alone does not pick a vehicle. Kemsley's four rows give 800;
the decoy 792 is the Rothwell vehicle's four rows, a real figure for the other vehicle,
and the claim was settled on the Kemsley one before the sum was taken.

## Five alternative phrasings of the task
1. aldersyde distribution vehicle t-14 september mileage
2. t-14 miles kemsley and rothwell depots
3. how many miles did t-14 cover in september
4. aldersyde fleet t-14 trip logs
5. vehicle t-14 mileage claim september
