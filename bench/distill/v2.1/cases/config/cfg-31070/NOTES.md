## Traps
- TR-CLAIM: list separator format and exact single-line replacement.
- 1 file(s) change, 0 stay byte-identical.

## Reference solution
1. read_lines
2. edit line 7
3. edit line 3
4. read back
5. read back the edited region and compare with the request

## Why the answer is unique
AllowedIPs two ranges, DNS 10.8.0.1.
Final answer should mention: 192.168.50.0/24; 10.8.0.1; 192.168.50.0/24
