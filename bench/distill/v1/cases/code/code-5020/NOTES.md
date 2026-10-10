## Traps
- TR-DECOY: the quench store defines its own helper with the same name, tally_draw, and crews/sorter.py calls that one, so counting every call named tally_draw in the crews modules gives 3 instead of 2.

## Reference solution
1. Read melt/store.py: it defines the glassworks' tally_draw for a draw (call 1).
2. Read crews/loader.py: it imports that helper from melt.store and calls it twice, in load() and reload() (call 2).
3. Read crews/sorter.py and quench/store.py: the sorter imports the quench store's own tally_draw, which is a different helper over the cooled draws (call 3). The two calls that go to the melt store's helper make the answer 2.

## Why the answer is unique
The decoy count 3 comes from treating the two helpers as one: quench/store.py appends to its own COOLED list and melt/store.py records a draw in DRAWS, and each caller binds the helper it means by the module it imports from. crews/sorter.py binds the quench helper, so its call is not a call of the melt store's function; the two calls in crews/loader.py are, and no other module calls it. The answer is 2.
