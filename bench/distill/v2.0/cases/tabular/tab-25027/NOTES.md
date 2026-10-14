## Traps
- TR-DECOY: the workspace holds the June export as well, and its largest burn came to 1184 kilograms. That figure
  is larger and sits in an identically shaped file, so a reader who scans both exports or reads the wrong one
  answers 1184 instead of 962.

## Reference solution
1. List the workspace: a June burn export, a July burn export and a short readme.
2. Read burn_log_2026-07.csv, the export for the month the request names.
3. The heaviest yield in that file is 962 kilograms, on burn CH-8847.

## Why the answer is unique
The question fixes the month, and the readme says the exports are one per month with one row per burn, so the
July figures live only in the July export. Every burn in that file has a single yield, and CH-8847 carries the
largest at 962 kilograms, which no other July row reaches. The bigger June burn belongs to another month and does
not describe a July burn, so it cannot answer the request.
