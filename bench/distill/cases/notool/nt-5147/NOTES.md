## Traps
- TR-NOTOOLNEED: the panel note and the bit weight sheet are in the workspace, but the eight bit weights are standing values and the switch bank is in the task; no file has to be opened. Reading the bank from the other end gives 75.

## Reference solution
No steps; ref_calls is 0. 11010010 sets bits 7, 6, 4 and 1, which is 128 + 64 + 16 + 2. The answer is 210.

## Why the answer is unique
Read left to right from bit 7, the bank 11010010 is 128 + 64 + 16 + 2 = 210. 75 is the same bank read right to left, with the 128 weight on the right; the panel's bank is read left to right from bit 7 down to bit 0, so the leftmost switch carries the 128 weight and the address is 210.
