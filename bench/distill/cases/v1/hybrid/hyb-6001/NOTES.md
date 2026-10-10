## Traps
- TR-AMBIG: the request names the Osprey while cruises/september-2026.csv holds two candidates, Osprey of Skerray and Osprey of Larnwick. Reading it as Osprey of Larnwick gives 120; the request was settled on Osprey of Skerray, giving 122 (from cruises/september-2026.csv). The data alone cannot say which candidate the request means, so the assistant has to ask before answering.

## Reference solution
1. Turn 1: the request names the Osprey but the workspace holds two candidates, Osprey of Skerray and Osprey of Larnwick, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds cruises/september-2026.csv and README.md.
3. read cruises/september-2026.csv and take the total of the passengers column for Osprey of Skerray: 122.

## Why the answer is unique
The decoy 120 belongs to Osprey of Larnwick; it answers a different candidate, and the request was settled on Osprey of Skerray before the count was taken.
Every row names its candidate in full, so no row counts for both, and no third reading of the file exists. The answer is 122.

## Five alternative phrasings of the task
1. pelagan cruises osprey passengers september 2026
2. sailings by the osprey of skerray in september
3. passenger totals per vessel pelagan harbour
4. osprey of larnwick and osprey of skerray sailings
5. september insurance figures for the osprey
