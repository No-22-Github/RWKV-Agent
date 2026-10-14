## Traps
- none: hold_hours is defined once, in the kiln section, and the prompt names
  both the key and the file. Base L0 of the edit family.

## Reference solution
1. Read config/kiln.yaml (path given in the prompt).
2. Change the hold_hours line from 6 to 8 and save; every other line stays
   byte-identical.

## Why the answer is unique
The whole-file equals check compares config/kiln.yaml against the original with
only the hold_hours value moved from 6 to 8, so a second edit, a reformat of
untouched lines or touching the shipping section all fail. hold_hours appears
exactly once and the shipping section holds unrelated keys, so there is exactly
one compliant final file.
