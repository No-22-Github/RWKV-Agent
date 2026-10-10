## Traps
- Page numbering starts at 1 but the offset treats it as 0-based.

## Reference solution
Read script, use (PAGE - 1) * PAGE_SIZE, read back.

## Why the answer is unique
Items 11-20 printed.
The fixed script prints:
item-11 bench
item-12 table
item-13 sofa
item-14 tray
item-15 basket
item-16 rack
item-17 hook
item-18 cart
item-19 bin
item-20 jar
