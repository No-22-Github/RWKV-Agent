## Traps
- TR-DECOY: The other property (slf4j 2.0.13) is already in sync; the jackson lines are about another library.

## Reference solution
1. Read the basis reports/bom.txt: the new value is 1.5.7.
2. Read pom.xml: line 2, `<logback.version>1.4.14</logback.version>`, is the one to change.
3. replace_lines line 2 with `<logback.version>1.5.7</logback.version>`; the rest of the line stays.
4. Read pom.xml back to confirm.
Final answer example: pom.xml now has logback.version 1.5.7, as the BOM report shows; slf4j was left alone. / DONE
Criteria: exact target file content; output contains DONE.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
