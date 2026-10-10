## Traps
- TR-DECOY: The schedule lists 22 (Maintenance, the file's current value) and 25 (Current, not LTS); the 2024 blog still recommends 22.

## Reference solution
1. Read the basis https://ember-runtime.dev/releases: the new value is 24.
2. Read .tool-versions: line 2, `ember 22`, is the one to change.
3. replace_lines line 2 with `ember 24`; the rest of the line stays.
4. Read .tool-versions back to confirm.
Final answer example: .tool-versions now has ember 24, the Active LTS on the release schedule; the other lines are untouched. / DONE
Criteria: exact target file content; output contains DONE.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.

## Five alternative phrasings of the task
1. Ember runtime release schedule
2. Ember runtime Active LTS
3. Ember runtime LTS version 2026
4. Ember runtime end of support
5. Ember runtime releases
