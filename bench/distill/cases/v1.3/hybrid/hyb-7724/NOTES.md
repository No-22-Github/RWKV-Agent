## Traps
- TR-NEARNAME: the request uses the retired kiln-log.csv name. The README pins the monthly
  sheets to kiln/firings-YYYY-MM.csv; a model that never finds them may answer from the
  glaze log's salient 23 test tiles instead of the 18 firings.

## Reference solution
1. list_files kiln/: the sheet on disk is firings-2026-09.csv.
2. read_file README.md: firings live at kiln/firings-YYYY-MM.csv; kiln-log.csv is retired.
3. read_file kiln/firings-2026-09.csv. Turn 1: 18 firings. Turn 2: cone-6 rows number 12. Turn 3: G-207 is the most frequent glaze among them. Turn 4: G-207 owns 5 of the cone-6 firings.
4. read_file glazes/glaze-log.md is optional context; the tiles count (23) answers nothing asked here. Turn 5: G-207's cone-6 hours 9.5 + 9.0 + 9.5 + 10.0 + 10.0 average 9.6.

## Why the answer is unique
The retired name resolves to nothing, the README pins the monthly naming, and the firings sheet is the only record of kiln firings - the glaze log counts test tiles (23), a different population. Within the sheet, cone-6 rows number 12 and G-207 appears on exactly five of them with hours 9.5, 9.0, 9.5, 10.0 and 10.0, whose average is 9.6; every step is a one-of count on distinct rows.

## Five alternative phrasings of the task
1. kilnwick pottery september kiln firings
2. how many firings ran in september
3. cone-6 firings in the september sheet
4. glaze code leading the cone-6 firings
5. average hours for that glaze's cone-6 firings
