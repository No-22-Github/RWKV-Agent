## Traps
- TR-AMBIG: the request names the Fen array while the movement files hold two arrays of that name, Turf Fen Array and Rush Fen Array. Reading it as Rush Fen Array gives 1620.5; the request was settled on Turf Fen Array, giving 1705. The files alone cannot say which array the yield return is for, so the assistant has to ask before computing.
- TR-MULTISRC: generation/september-2026.csv alone gives 1842.5 for Turf Fen Array. The README nets curtailed energy off the yield and curtailment/september-2026.csv records 137.5 for that array, so the yield is 1705.

## Reference solution
1. Turn 1: the request names the Fen array but the workspace holds two candidates, Turf Fen Array and Rush Fen Array, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds generation/september-2026.csv, curtailment/september-2026.csv and README.md.
3. read README.md: each array reports against its own meter registration and the yield nets off energy the grid operator curtailed.
4. read generation/september-2026.csv and total the kilowatt hours Turf Fen Array generated.
5. read curtailment/september-2026.csv and total the curtailed amounts for Turf Fen Array.
6. subtract the curtailment: the net yield is 1705.

## Why the answer is unique
The decoy 1620.5 is Rush Fen Array's own net; it answers a different array, and the request was settled on Turf Fen Array before any figure was taken.
The decoy 1842.5 counts only what Turf Fen Array generated. The README states the yield figure nets off curtailment, and every curtailment row in curtailment/september-2026.csv names that array, so leaving them out contradicts the stated basis.
Every row carries the array's full name, so no row belongs to both candidates and no third reading of the files exists. The answer is 1705.

## Five alternative phrasings of the task
1. fenby community energy fen array september 2026
2. generation for turf fen array and rush fen array
3. yield per array with curtailment netted off
4. september meter registration return fenby
5. kilowatt hours by array at fenby
