## Traps
- BOM glued to the first header makes row['sku'] a KeyError.

## Reference solution
Read script, change encoding to utf-8-sig, read back.

## Why the answer is unique
utf-8-sig strips the BOM from the first header.
The fixed script prints:
A-100	34
B-220	20
C-310	10
