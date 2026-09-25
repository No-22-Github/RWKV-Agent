## Traps
- TR-NOTOOLNEED: the weight sheet sits in the standards folder and the controller file sits in the panels folder, but hexadecimal place values are standing arithmetic; no file has to be opened. Weighting the digits by ten instead of sixteen gives 1154.

## Reference solution
No steps; ref_calls is 0. The address B4E reads, highest digit first, as B (11) lots of 256, 4 lots of 16 and E (14) ones: 11 x 256 + 4 x 16 + 14. The answer is 2894.

## Why the answer is unique
Hexadecimal digits carry place values of sixteen, so B4E is 2,816 + 64 + 14 = 2,894. 1154 comes from reading the same three digits with place values of ten (11 x 100 + 4 x 10 + 14), which is denary arithmetic applied to a hexadecimal keypad; the register holds the address the controller actually carries, so the answer is 2894.
