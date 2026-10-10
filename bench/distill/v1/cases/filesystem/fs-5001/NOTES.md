## Traps
- TR-DECOY: screening-mon.txt is a near copy of the Friday sheet, identical line for line except the bar float line, which reads "Bar float: 120.00 taken at 18:20." against "taken at 18:50." in screening-fri.txt. Comparing the sheets by resemblance instead of by bytes reports screening-mon.txt, which is the wrong answer.

## Reference solution
1. list_files (1): four files - README.md and three sheets, screening-fri.txt, screening-mon.txt, screening-sat.txt.
2. read_file screening-fri.txt (2): the reference sheet, eight lines including its blank line.
3. read_file screening-mon.txt (3): every line matches the reference except the bar float line, so it is not the copy.
4. read_file screening-sat.txt (4): every byte matches the reference, so it is the copy and the answer is screening-sat.txt.

## Why the answer is unique
The question asks for a byte-for-byte copy of screening-fri.txt, so the test is equality of bytes, not resemblance. screening-mon.txt fails that test: its bar float line reads "taken at 18:20." while the reference reads "taken at 18:50.", a one character difference, so the two files are not equal and it cannot be the copy. The only other file whose bytes equal the reference is screening-sat.txt. README.md is prose about the folder and carries none of the sheet lines; there is no fourth sheet. Exactly one file in the folder qualifies, so the answer is screening-sat.txt.
