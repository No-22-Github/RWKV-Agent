## Traps
- TR-DECOY: Unreleased mentions v4; the 1.8.0 entry gives v2, the file's current value.

## Reference solution
1. Read the basis CHANGELOG.md: the new value is 3.
2. Read internal/proto/version.go: line 4, `const WireVersion = 2`, is the one to change.
3. replace_lines line 4 with `const WireVersion = 3`; the rest of the line stays.
4. Read internal/proto/version.go back to confirm.
Final answer example: WireVersion in internal/proto/version.go is now 3, from the 1.9.0 entry; the Unreleased v4 is not merged. / DONE
Criteria: exact target file content; output contains DONE.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
