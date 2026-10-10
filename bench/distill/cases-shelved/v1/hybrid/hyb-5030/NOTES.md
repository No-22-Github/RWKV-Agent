## Traps
- TR-EARLYHIT: the first result is the packaging standard's crate weights and its snippet
  gives the standard crate tare (2.5 kg) outright, so one search is enough and the case
  caps web_search at 1. The other page prices the heavy duty export crate at 3.4 kg; it is
  the decoy, and using it gives 2519.5 instead of the net fruit weight.

## Reference solution
1. list_files: the workspace holds consignments/september-2026.csv and README.md.
2. read_file consignments/september-2026.csv: four consignments, all packed in standard
   crates, with crates and gross_kg on every row; the README says the gross weight
   includes the crates.
3. web_search "standard crate weight": the packaging standard's first result gives the
   standard crate as 2.5 kg empty.
4. Take the tare off each consignment and add: (1012.0 - 100.0) + (632.5 - 62.5) +
   (810.0 - 80.0) + (456.0 - 45.0) = 912.0 + 570.0 + 730.0 + 411.0 = 2623.0.

## Why the answer is unique
The crate type is fixed by the consignment file itself, and every row names the standard
crate, so the standard crate's weight is the one that applies. The packaging standard
gives one weight per crate type and the export crate's 3.4 kg belongs to a crate no
consignment used; taking it off would answer for a crate the packhouse does not ship. The
net figure is 2623.0 kilograms.

## Five alternative phrasings of the task
1. standard crate weight soft fruit packaging
2. standard and export crate weights
3. how much does a crate weigh empty
4. soft fruit crate tare weight
5. crate weights pack standards bureau
