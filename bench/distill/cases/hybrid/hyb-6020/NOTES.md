## Traps
- TR-AMBIG: the request names the Orchard array while the movement files hold two arrays of that name, Orchard End Array and Orchard Wood Array. Reading it as Orchard Wood Array gives 1988.25; the request was settled on Orchard End Array, giving 2168.75. The files alone cannot say which array the members' pack note is for, so the assistant has to ask before computing.
- TR-MULTISRC: output/august-2026.csv alone gives 2287.25 for Orchard End Array. The README nets spilled energy off the output and spill/august-2026.csv records 118.5 for that array, so the net figure is 2168.75.

## Reference solution
1. Turn 1: the request names the Orchard array but the workspace holds two candidates, Orchard End Array and Orchard Wood Array, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds output/august-2026.csv, spill/august-2026.csv and README.md.
3. read README.md: each array reports against its own meter registration and output nets off the energy spilled under the local grid constraint.
4. read output/august-2026.csv and total the kilowatt hours Orchard End Array generated.
5. read spill/august-2026.csv and total the spilled amounts for Orchard End Array.
6. subtract the spill: the net figure is 2168.75.

## Why the answer is unique
The decoy 1988.25 is Orchard Wood Array's own net; it answers a different array, and the request was settled on Orchard End Array before any figure was taken.
The decoy 2287.25 counts only what Orchard End Array generated. The README states the output nets off spill, and every spill row in spill/august-2026.csv names that array, so leaving them out contradicts the stated basis.
Every row carries the array's full name, so no row belongs to both candidates and no third reading of the files exists. The answer is 2168.75.

## Five alternative phrasings of the task
1. witherslack solar orchard array august 2026
2. output for orchard end array and orchard wood array
3. yield per array with spill netted off
4. august members pack figures witherslack
5. kilowatt hours by array at witherslack
