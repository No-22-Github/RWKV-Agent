## Traps
- TR-DECOY: src/api.py 底部有一行注释掉的 reserve_stock 调用，按文本搜索会多算一处、答成三处调用。 A careless pass reports `3`.

## Reference solution
1. Read src/inventory.py to locate the definition.
2. Read src/api.py and src/flows.py for call sites, treating the commented shim as dead text.
3. List the calling functions and the defining file.

## Why the answer is unique
The commented shim in api.py is dead text and no executable path follows it, so the live call sites are exactly reserve_endpoint in api.py and restock_low_items in flows.py. The definition of reserve_stock sits in inventory.py, and no other file touches it.
