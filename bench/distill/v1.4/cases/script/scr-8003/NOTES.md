## Traps
- Path.glob('*.txt') is non-recursive.

## Reference solution
Read the script, list visits/, change glob to rglob, read back.

## Why the answer is unique
rglob covers main.txt and every satellite folder.
The fixed script prints:
Dr. Lindqvist=2
Dr. Okafor=3
Dr. Reyes=3
