## Traps
- TR-RULEFILE: the array rule lives in docs/merge-guide.md — arrays are
  replaced whole, never concatenated. Concatenating the base list (three sites)
  with the patch list (two sites) reports 5; reading only the base reports 3.
  The guide's rule makes the merged regions the patch's own list.

## Reference solution
1. Read docs/merge-guide.md (path given in the prompt): same-name keys follow
   the patch; arrays are replaced whole.
2. Read config/monitor-base.json: the baseline regions list has three sites.
3. Read vendor/upgrade-patch.json: the patch's regions list has two sites and
   replaces the baseline list whole, so the merged array has 2 sites.

## Why the answer is unique
The guide is stated to govern the merge, and its array rule admits no middle
ground: the merged list is exactly the patch's list, so its length is 2. The
concatenation reading (5) contradicts rule three outright, and the base-only
reading (3) contradicts rule one; no other merge order is offered by the guide,
so no other count is defensible.
