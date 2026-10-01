## Traps
- TR-NEARNAME: the request uses the retired delay-log.csv name. The handbook points to
  site/delays-YYYY-MM.csv; a model that grabs the nearest existing sheet takes
  site/delays-2026-08.csv, whose total is 27 instead of 28.

## Reference solution
1. list_files site/: two monthly delay sheets sit there.
2. read_file docs/install-handbook.md: the monthly sheets are site/delays-YYYY-MM.csv and delay-log.csv is gone.
3. read_file site/delays-2026-09.csv. Turn 1: 28 delay days. Turn 2: Ashcroft Tower tops the sheet with 12. Turn 3: weather rows sum to 12.

## Why the answer is unique
The August sheet is the nearest look-alike but answers a different month, and the handbook plus the prompt's September ask pin the sheet to delays-2026-09.csv. Within it, Ashcroft Tower's 12 leads Lantern Court's 9, and the weather rows (5 + 3 + 2 + 2) are the only cause summing to 12, so 28, Ashcroft Tower and 12 are the only readings.

## Five alternative phrasings of the task
1. kestrel windows september delay sheet
2. delay days recorded in september
3. which site caused the most delay days
4. september delays from weather holds
5. site delay totals for the september review
