## Traps
- None. No trap tag is set: one module imports and calls the helper, and only one module defines it.

## Reference solution
1. Read bench/sorting.py: it imports weigh_bundle from scales.bundles (call 1).
2. Read scales/bundles.py and find the definition of weigh_bundle (call 2).

## Why the answer is unique
The bench binds the helper as `from scales.bundles import weigh_bundle` and scales/bundles.py is
where `def weigh_bundle(bundle)` sits; scales/__init__.py only carries the package notes. No other
module defines or binds the helper. The answer is scales/bundles.py.
