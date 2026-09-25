## Traps
- TR-DEFN: every record carries two times. The first stamp is the conspicuous one, when the record reached the office, and the window does not belong to it; `at`, the time the barrier registered the crossing, is the time the question asks about. Counting by the first stamp gives 6 instead of 15.

## Reference solution
1. List the workspace: README.md and logs/bridge-crossings.log.
2. Read README.md: `at` is when the barrier registered the crossing, the first stamp is when the record reached the office, and the barrier holds its records while the link is down and sends them in batches.
3. Read logs/bridge-crossings.log and count the records whose `at` falls between 06:00 and 09:00 on 6 September 2026: 15 of them.

## Why the answer is unique
README.md says the first stamp is the upload time and `at` is the crossing time, so the window asked for, the morning's traffic, is measured on `at`; the upload stamps are later and land in batches, which is why they cannot stand for the crossing time. Fifteen records carry an `at` inside the window. The decoy 6 is what the window holds when it is applied to the first stamp instead, and 25 is the whole day's traffic. With the crossing time used, the answer is 15.

## Fixture notes
Every record carries both stamps on 6 September 2026 and the closing line makes the file self-checking. The upload stamps come in three batches, so ordering the file by the first stamp does not order it by crossing time, and no crossing is registered exactly on a window edge. `weight` varies with the vehicle and is unrelated to the count.
