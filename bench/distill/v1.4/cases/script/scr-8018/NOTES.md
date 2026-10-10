## Traps
- json.load rejects a UTF-8 BOM when the file is opened as plain utf-8.

## Reference solution
Read script, open with utf-8-sig, read back.

## Why the answer is unique
BOM is tolerated; all stores are merged.
The fixed script prints:
拖鞋 50
毛巾 42
牙刷 130
