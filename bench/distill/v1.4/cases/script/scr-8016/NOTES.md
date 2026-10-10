## Traps
- A UTF-8 BOM is glued to the first header, so the key is '\ufeff姓名' and row['姓名'] raises KeyError.

## Reference solution
Read script, change encoding to utf-8-sig, read back.

## Why the answer is unique
utf-8-sig strips the BOM.
The fixed script prints:
周岚 96 小时
孙敏 160 小时
李想 148 小时
钱程 192 小时
