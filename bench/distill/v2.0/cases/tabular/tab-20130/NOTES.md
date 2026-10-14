## Traps
- No calculator: work the arithmetic out and show the working, or do it in the shell with awk.

## Reference solution
bash: awk '{printf "%.2f\n", $2*0.85-30}' price.txt -> 733.73

## Why the answer is unique
898.50 * 0.85 - 30.
