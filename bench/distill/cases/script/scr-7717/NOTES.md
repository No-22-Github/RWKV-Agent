## Traps
- TR-DATEFMT: the October file (the scoring run's hidden input) is written by the paper app in day-first slashes; 06/10/2026 is 6 October and must be kept by --since 2026-10-05. Reading slashes month-first turns it into June, drops the day, and the report starts at 2026-10-11 with TOTAL 5800 instead of 9400.

## Reference solution
1. Read pledges.py: the layout and the ISO day spelling are pinned by the docstring.
2. Read pledges/2026-09.csv to confirm the columns (September is all phone-app ISO).
3. Read README.md: the paper app writes day-first slashes, both spellings mean the same day.
4. Add the --since flag with day parsing for both spellings; days still print in ISO, and the no-flag behavior stays exactly as it is.

## Why the answer is unique
With both spellings parsed day-first where slashed, the merged run filtered from 2026-10-05 onward prints exactly 2026-10-06,3600 / 2026-10-11,1900 / 2026-10-18,2600 / 2026-10-25,1300 and TOTAL,9400. The README states the paper app writes day-first slashes, so dropping 6 October is a misreading of the station's own convention; a --since that string-compares the raw cells would also drop it, and the docstring keeps the ISO spelling on the report either way.
