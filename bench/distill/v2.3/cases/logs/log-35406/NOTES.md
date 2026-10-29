## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: bash, search_text).

## Reference solution
read_file logs/nightly-export-0912.log (46 lines, one screen) -> count the WARN lines by eye: 7

## Why the answer is unique
46 lines, level is the token after the timestamp; INFO lines say '0 warnings' as a lowercase decoy.

Expected: 7
