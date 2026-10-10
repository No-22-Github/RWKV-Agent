## Traps
- TR-DECOY: workshop/varnish-2026-09.log interleaves V-300 (current) and V-200 (previous)
  batch lines with similar codes. All fault lines total 24; the V-300 series subset is 14.

## Reference solution
1. read_file README.md: fault lines name the cure fault; note lines are shop conditions.
2. read_file docs/batch-codes.md: V-300 is the current series, V-200 the previous one.
3. read_file workshop/varnish-2026-09.log. Turn 1: V-3xx fault lines number 14 (clouding 10, blistering 2, tackiness 2). Turn 2: clouding is the most frequent among them. Turn 3: V-301, 303, 305, 307, 309 logged clouding = 5 batches. Turn 4: V-200 clouding lines number 8.

## Why the answer is unique
Counting every fault line gives 25, but the batch registry separates the two series and the request names V-300, so the ten V-200 faults answer a different question. Within V-300, clouding appears 10 times across exactly five batches, ahead of blistering (2) and tackiness (2); the V-200 clouding count is 8, distinct from its 10 total faults.

## Five alternative phrasings of the task
1. ostrander violins september varnish faults
2. cure faults on the v-300 series batches
3. most frequent cure fault in the new series
4. batches hit by clouding in the new formula
5. clouding count for the old v-200 series
