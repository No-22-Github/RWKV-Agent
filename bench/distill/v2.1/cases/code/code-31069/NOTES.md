## Traps
- TR-CLAIM: $ must survive; only the glob changes in turn 2.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_file
2. edit last line
3. edit glob
4. cat script
5. read back the edited region and compare with the request

## Why the answer is unique
Final script as expected.
Final answer should mention: cleaned $TARGET; *.cache; done
