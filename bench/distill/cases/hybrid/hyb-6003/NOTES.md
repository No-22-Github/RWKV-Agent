## Traps
- TR-AMBIG: the request names The Sail Loft while hires/august-2026.csv holds two candidates, Cove Street and Quay Lane. Reading it as Quay Lane gives 6; the request was settled on Cove Street, giving 5 (from hires/august-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names The Sail Loft but the workspace holds two candidates, Cove Street and Quay Lane, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds hires/august-2026.csv and README.md.
3. read hires/august-2026.csv and take the count of rows for Cove Street: 5.

## Why the answer is unique
The decoy 6 belongs to Quay Lane; it answers a different candidate, and the request was settled on Cove Street before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 5.

## Five alternative phrasings of the task
1. pennycross heritage trust sail loft bookings august 2026
2. room hire at cove street and quay lane
3. how busy was the sail loft in august
4. sail loft booking diary pennycross
5. august hires for the two sail loft rooms
