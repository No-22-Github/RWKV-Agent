## Traps
- none: the README pins the only effective config file and auto_close_days is
  defined once, so the base L0 of the edit family is locate-then-edit.

## Reference solution
1. Read README.md: the effective config is config/repair-desk.json.
2. Read config/repair-desk.json: auto_close_days is 7.
3. Change the auto_close_days line from 7 to 10 and save; every other line
   stays byte-identical.

## Why the answer is unique
The whole-file equals check compares config/repair-desk.json against the
original with only the auto_close_days value moved from 7 to 10, so a second
edit, a reformat of untouched lines or editing a different file all fail.
auto_close_days appears exactly once and no other key is about closing tickets,
so there is exactly one compliant final file.
