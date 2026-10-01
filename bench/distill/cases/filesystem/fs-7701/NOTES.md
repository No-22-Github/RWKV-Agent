## Traps
- TR-DECOY: the same file name print-index.csv exists in catalog/ (current season, 6 rows) and archive/ (closed 2024 season, 4 rows). Reading the archive copy or adding the two together gives 4 or 10 prints; README says client-facing counts come from catalog/ only.

## Reference solution
1. List the folder: print-index.csv appears in catalog/ and archive/.
2. Read README.md: catalog/ is the current season, archive/ is the closed 2024 season under the same name; client counts come from catalog/.
3. Read catalog/print-index.csv: 6 prints, 3 on luster paper; read archive/print-index.csv: 4 archived prints.

## Why the answer is unique
The decoy 10 prints sums both indexes, and 4 prints is the archive copy taken alone. README assigns print-index.csv in archive/ to the closed 2024 season and states counts quoted to clients come from catalog/ only, so neither the archive rows nor their sum can be the current count; it can only be 6. The paper column of the catalog has exactly 3 luster rows, and the archive file holds exactly 4 rows. Which file is current is decided by the README rule, so the three facts have no second reading.
