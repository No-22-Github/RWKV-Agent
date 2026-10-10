## Traps
- TR-PRECEDENCE: the three layers apply in the order base, winter fragment,
  tower file; the tower file does not write lift_quota, so the fragment's list
  stands for Annan. Reading only the base reports 2.
- TR-RULEFILE: the README states arrays are replaced whole, never
  concatenated; concatenating the base list with the fragment list reports 5.

## Reference solution
1. Read README.md (path given in the prompt names the two upper files): the
   apply order, the whole-array rule, and that a layer not writing a key keeps
   the previous result.
2. Read config/winter-fragment.json: its lift_quota lists three towers and, by
   the array rule, replaces the base list whole.
3. Read config/tower-annan.json: it writes only ev_charge_slots, so the
   effective lift_quota for Annan is the fragment's list of 3 towers.

## Why the answer is unique
The README fixes both the layer order and the array rule: the merged list is
the last list written to lift_quota, which is the fragment's, and the tower
layer writes nothing to that key. The concatenation reading (5) contradicts the
stated array rule, and the base-only reading (2) contradicts the stated layer
order; no other reading of the three files yields a different count, leaving 3.
