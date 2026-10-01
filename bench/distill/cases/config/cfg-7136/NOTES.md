## Traps
- TR-RULEFILE: docs/queue-merge.txt says nested objects merge key by key and
  sub-keys the fragment does not write keep the baseline value. Treating the
  fragment's retry object as a whole-object replacement drops max_attempts from
  view and pushes a solver toward quoting the fragment's backoff_s figure (5)
  instead of the asked key.

## Reference solution
1. Read docs/queue-merge.txt (path given in the prompt): nested objects merge
   key by key; unlisted keys keep the baseline value.
2. Read config/farm-base.json: retry carries max_attempts 4 and backoff_s 9.
3. Read config/queue-fragment.json: its retry names only backoff_s (5), so
   max_attempts keeps the baseline value 4.

## Why the answer is unique
The guide is stated to govern the merge, and its nested-object rule keeps every
sub-key the fragment does not mention, so max_attempts survives with the
baseline value 4. Whole-object replacement is not among the guide's rules and
neither is dropping the key, and the fragment's 5 is the backoff figure for a
different key, so no reading makes anything but 4 the merged max_attempts.
