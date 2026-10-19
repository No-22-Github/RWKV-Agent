## Traps
Large files hide in different subfolders; the other 307 files are all below 1800 bytes.

## Reference solution
find -printf '%s %p' | sort -rn | head -3.

## Why the answer is unique
The three planted files exceed 3400 bytes, all others are below 1900. Expected answer per turn: part_1331.log/part_0242.txt/part_5768.bin.
