## Traps
- TR-DECOY: loft/labels.py binds bend_sail but never calls it, so naming the module that imports
  the helper gives loft/labels.py.

## Reference solution
1. Read the modules under the loft and find the one that binds bend_sail (call 1).
2. Keep the module that also calls it: loft/bending.py bends the sail, while loft/labels.py only
   labels sails and never calls the helper (call 2).
3. store/rigging.py is where bend_sail is defined (call 3).

## Why the answer is unique
Only loft/bending.py both binds the helper and calls it. loft/labels.py carries the same import
but no call, so it cannot be the module that bends a sail. The answer is loft/bending.py.
