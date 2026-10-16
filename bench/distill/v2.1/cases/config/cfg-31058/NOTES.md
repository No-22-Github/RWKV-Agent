## Traps
- TR-CLAIM: forgetting the comma after author leaves invalid JSON.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines
2. replace last-but-one line with comma, add license line
3. read back the edited region and compare with the request

## Why the answer is unique
File ends with author comma + license.
Final answer should mention: license; MIT; Mara Ito
