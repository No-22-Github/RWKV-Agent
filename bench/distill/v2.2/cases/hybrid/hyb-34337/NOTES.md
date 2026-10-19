## Traps
TR-DEFN

## Reference solution
Bits needed. ceil(log2(50000)) = 16 (2^15 = 32768 < 50000 <= 65536 = 2^16). The calculator has ln and log10 but no log2.

## Why the answer is unique
Recomputed by verify.py from the numbers in the prompt. Expected: 16.0 (16; 16 / 16)

## Five alternative phrasings of the task
1. 50000 个用户的编号要几位二进制
2. 二进制位数 log2(50000) 向上取整
3. 给五万人编号至少几比特
4. 唯一编号的最短二进制长度
5. minimum bits for 50000 unique ids
