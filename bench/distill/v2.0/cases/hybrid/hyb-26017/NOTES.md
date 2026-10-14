## Traps
- TR-AMBIG: the request names the Badger while the movement files hold two vans of that name, Northgate Badger and Southgate Badger. Reading it as Southgate Badger gives 33; the request was settled on Northgate Badger, giving 38. The files alone cannot say which van the invoice is for, so the assistant has to ask before computing.
- TR-MULTISRC: outbound/september-2026.csv alone gives 47 for Northgate Badger. The README credits unused pallets to the van that ran them and returns/september-2026.csv records 9 of them under that van, so the net is 38.

## Reference solution
1. Turn 1: the request names the Badger but the workspace holds two candidates, Northgate Badger and Southgate Badger, so the assistant asks which is meant and calls no tool.
2. list_files: the workspace holds outbound/september-2026.csv, returns/september-2026.csv and README.md.
3. read README.md: the grower contract is invoiced per vehicle and pallets coming back unused are credited to the van that carried them out.
4. read outbound/september-2026.csv and total the pallets Northgate Badger moved out.
5. read returns/september-2026.csv and total the pallets credited back to Northgate Badger.
6. subtract the returns: the invoice figure is 38.

## Why the answer is unique
The decoy 33 is Southgate Badger's own net; it answers a different van, and the request was settled on Northgate Badger before any figure was taken.
The decoy 47 counts only what Northgate Badger moved out. The README states the credit for returns, and every return row in returns/september-2026.csv names that same van, so leaving them out contradicts the stated basis.
Every row carries the van's full name, so no row belongs to both candidates and no third reading of the files exists. The answer is 38.

## Five alternative phrasings of the task
1. arrowfield haulage badger pallets september 2026
2. movement for northgate badger and southgate badger
3. pallets out and returns per van arrowfield
4. september invoice pallets net of returns
5. grower contract movement by vehicle
