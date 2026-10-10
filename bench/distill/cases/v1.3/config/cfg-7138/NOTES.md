## Traps
- none: cooling_minutes is defined once and the target value is named in the
  prompt. Base L0 of the edit family.

## Reference solution
1. Read config/drying.yaml (path given in the prompt).
2. Change the cooling_minutes line from 60 to 90 and save; every other line
   stays byte-identical.

## Why the answer is unique
The whole-file equals check compares config/drying.yaml against the original
with only the cooling_minutes value moved from 60 to 90, so a second edit, a
reformat of untouched lines or a missed edit all fail. cooling_minutes appears
exactly once, and no other line carries a value the prompt asks to change, so
there is exactly one compliant final file.
