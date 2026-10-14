## Traps
- os.listdir is flat; rotated logs are in subfolders.

## Reference solution
Read errcount.py, list logs/, replace the loop with os.walk, read back.

## Why the answer is unique
os.walk visits rotated/ and rotated/old/ as well as the top level.
The fixed script prints:
api: 3
billing: 2
worker: 2
