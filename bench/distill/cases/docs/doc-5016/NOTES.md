## Traps
- TR-ABSENT: the charges sheet lists a packing service, a piano move, wardrobe box hire, storage and an extra stop, and it has no row for taking a fitted wardrobe down and putting it back together. The neighbouring row `Wardrobe box hire each` is 21.50, and a solver that reads that row as covering the customer's request reports 21.50 instead of UNKNOWN.

## Reference solution
1. List the workspace, then read fees/charges.csv and README.md.
2. fees/charges.csv prices five services — packing, a piano move, wardrobe box hire, storage and an extra stop — and has no row for taking a fitted wardrobe down and putting it back together; README.md states that work the sheet does not list is quoted by the office once the move has been surveyed, so no charge for the fitted wardrobe work exists in the folder.
3. Final answer in two or three sentences: name the files checked, say there is no charge for fitted wardrobe disassembly and reassembly, and point to wardrobe box hire as a different item without quoting its figure. Scored with output_contains_any over "fitted wardrobe", "fitted wardrobe disassembly and reassembly" or "taking a fitted wardrobe down"; output_excludes rules out UNKNOWN and the 21.50 wardrobe-box-hire figure, so the reply names the missing service instead of quoting any charge.

## Why the answer is unique
The sheet is the firm's complete price list and README.md states how unlisted work is priced, so a service with no row has no figure to report. The decoy 21.50 is the wardrobe box hire charge, which prices a box the customer packs rather than work on a fitted wardrobe, so reading one as the other is the mistake the case is built around. The only truthful reply reports the absence: fees/charges.csv and README.md were checked, no fitted wardrobe row exists among the listed services, and the neighbouring wardrobe entry is a different item whose charge is not the answer to the question.
