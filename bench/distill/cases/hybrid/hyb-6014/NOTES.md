## Traps
- TR-AMBIG: the request names The Coach House while viewings/june-2026.csv holds two candidates, Harrow Lane and Harrow Rise. Reading it as Harrow Rise gives 3; the request was settled on Harrow Lane, giving 8 (from viewings/june-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names The Coach House but the workspace holds two candidates, Harrow Lane and Harrow Rise, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds viewings/june-2026.csv and README.md.
3. read viewings/june-2026.csv and take the count of rows for Harrow Lane: 8.

## Why the answer is unique
The decoy 3 belongs to Harrow Rise; it answers a different candidate, and the request was settled on Harrow Lane before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 8.

## Five alternative phrasings of the task
1. tarnside residential coach house viewings june 2026
2. viewings at harrow lane and harrow rise
3. coach house viewing counts tarnside
4. june summary for the coach house landlord
5. accompanied viewings per landlord tarnside
