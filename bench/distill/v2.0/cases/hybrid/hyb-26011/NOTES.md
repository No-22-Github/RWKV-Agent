## Traps
- TR-AMBIG: the request names the Wren while journeys/september-2026.csv holds two candidates, Grey Wren and Blue Wren. Reading it as Blue Wren gives 172.3; the request was settled on Grey Wren, giving 193 (from journeys/september-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the Wren but the workspace holds two candidates, Grey Wren and Blue Wren, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds journeys/september-2026.csv and README.md.
3. read journeys/september-2026.csv and take the total of the miles column for Grey Wren: 193.

## Why the answer is unique
The decoy 172.3 belongs to Blue Wren; it answers a different candidate, and the request was settled on Grey Wren before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 193.

## Five alternative phrasings of the task
1. struan activity college wren miles september 2026
2. journey log for blue wren and grey wren
3. miles per minibus struan college
4. september fuel claim sheets by vehicle
5. minibus mileage for the two wrens
