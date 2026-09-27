## Traps
- TR-AMBIG: the request names Clover while rides/september-2026.csv holds two candidates, Grey Clover and Bay Clover. Reading it as Bay Clover gives 5; the request was settled on Grey Clover, giving 6 (from rides/september-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names Clover but the workspace holds two candidates, Grey Clover and Bay Clover, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds rides/september-2026.csv and README.md.
3. read rides/september-2026.csv and take the count of rows for Grey Clover: 6.

## Why the answer is unique
The decoy 5 belongs to Bay Clover; it answers a different candidate, and the request was settled on Grey Clover before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 6.

## Five alternative phrasings of the task
1. halcyon riding school clover rides september 2026
2. ride diary for grey clover and bay clover
3. pony worklog at the riding school
4. september rides per pony halcyon
5. welfare check ride counts for clover
