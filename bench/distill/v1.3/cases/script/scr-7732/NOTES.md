## Traps
- TR-MULTISRC: the netted sheet needs pickers/ and returns/ together; reading only the picker exports prints gross kg (decoy: gross picked kg without the shed returns)
- The scoring run also adds pickers/2026-10.csv, returns/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read day_sheet.py: the docstring fixes the netting (picked kg minus returned kg per date, returns-only dates print with zero sacks).
2. Read README.md to confirm the two folders and the netting rule.
3. Read pickers/2026-09.csv to confirm the sack columns.
4. Read returns/2026-09.csv to confirm the return columns.
5. Write day_sheet.py: sum picks and returns per date across both folders, print each date in order as date,sacks,net_kg, then TOTAL.

## Why the answer is unique
The docstring nets the two folders per date, so 2026-09-03 prints 2,287 (323 picked minus 36 returned) and the returns-only 2026-09-24 prints 0,-29; the sheet ends TOTAL,9,1155. Reading only pickers/ prints the gross kg and never produces the returns-only date line, and the scoring run adds an October export to each folder, so a one-folder script differs there too.
