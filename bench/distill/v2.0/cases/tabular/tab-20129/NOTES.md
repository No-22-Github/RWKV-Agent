## Traps
- No calculator: work the arithmetic out and show the working, or do it in the shell with awk.

## Reference solution
bash: awk '{s+=$3*$5} END{printf "%.2f\n", s}' 报价/报价单.txt -> 815.07

## Why the answer is unique
Three lines, price times quantity, summed.
