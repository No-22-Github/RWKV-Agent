## Traps
- TR-DECOY: `queue/handoff.py` imports seal_lot from the lot store and never calls it, so answering from the import lines alone points at the wrong module. Only `packing/sealer.py` has both the binding and the call.

## Reference solution
1. Read roast/store.py: seal_lot is the module's definition and it calls nothing (call 1).
2. Read queue/handoff.py: it binds the name with an import but its only function returns a label, so it never calls seal_lot (call 2).
3. Read packing/sealer.py: it binds the name and calls it inside seal_finished (call 3). The answering module is packing/sealer.py.

## Why the answer is unique
The decoy module names seal_lot in its import and nowhere else, so it produces no sealed lot; the store module defines the function without calling it. The only module that both binds and calls the name is packing/sealer.py, and every lot it seals goes through that one call. The answer is packing/sealer.py.
