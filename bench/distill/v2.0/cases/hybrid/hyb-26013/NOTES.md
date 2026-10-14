## Traps
- TR-AMBIG: the request names the Garden Flat while viewings/september-2026.csv holds two candidates, Ferndale Road and Ferndale Lane. Reading it as Ferndale Lane gives 3; the request was settled on Ferndale Road, giving 4 (from viewings/september-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the Garden Flat but the workspace holds two candidates, Ferndale Road and Ferndale Lane, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds viewings/september-2026.csv and README.md.
3. read viewings/september-2026.csv and take the count of rows for Ferndale Road: 4.

## Why the answer is unique
The decoy 3 belongs to Ferndale Lane; it answers a different candidate, and the request was settled on Ferndale Road before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 4.

## Five alternative phrasings of the task
1. byrewood lettings garden flat viewings september 2026
2. viewings at ferndale road and ferndale lane
3. garden flat viewing counts byrewood
4. september statement for the garden flat landlord
5. accompanied viewings per property byrewood
