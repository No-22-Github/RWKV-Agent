## Traps
- isdir -> continue skips whole subfolders.

## Reference solution
Read script, list manifest/, switch to os.walk, read back.

## Why the answer is unique
os.walk sums every manifest at any depth.
The fixed script prints:
春季外拍	4800
社团迎新	6000
秋季外拍	11600
