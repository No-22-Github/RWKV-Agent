## Traps
- TR-EARLYHIT: the first result is Pellbrook Spring's own tariff page and its snippet gives
  the bulk rate (89 pence per cubic metre), so one search is enough and the case caps
  web_search at 1. The bottling line tariff is the decoy: its 41 pence applies to water
  metered on the bottling line, which that page says is never added to the bulk reading.

## Reference solution
1. list_files: the workspace holds meter/bulk-2026-09.csv and README.md.
2. read_file meter/bulk-2026-09.csv: the four September weeks hold 9, 11, 8 and 13 cubic
   metres, so the metered volume is 41.
3. web_search "pellbrook bulk water tariff": the tariff page is the first result and its
   snippet gives 89 pence per cubic metre for the bulk tariff.
4. Multiply: 41 x 89 = 3649 pence.

## Why the answer is unique
The meter sheet is the bulk supply's own reading and the tariff page prices the bulk
tariff on the metered volume, so the charge is the September volume times 89 pence:
3649. The bottling line page prices a different meter at 41 pence and states that the two
readings are never added together, so its figure cannot apply to the bulk volume the
plant drew in September.

## Five alternative phrasings of the task
1. pellbrook spring bulk water tariff
2. pellbrook bulk tariff pence per cubic metre
3. pellbrook spring september water charge
4. pellbrook spring bottling line tariff
5. cost of the pellbrook bulk supply in september
