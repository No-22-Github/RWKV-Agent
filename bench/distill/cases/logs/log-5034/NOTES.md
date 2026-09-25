## Traps
- TR-DEFN: every record carries two weights. `gross_kg` is the larger, more conspicuous one, the weighbridge reading with the pallets on board; the question asks for the produce, which is `net_kg`. Totalling the gross weights gives 1213200 instead of 1134000.

## Reference solution
1. List the workspace: README.md and logs/dispatch.jsonl.
2. Read README.md: `gross_kg` is the weighbridge reading with the pallets on board and `net_kg` is the produce alone, the pallets having been weighed off first.
3. Read logs/dispatch.jsonl and total the `net_kg` column over the 48 records of the day: 1134000 kilograms.

## Why the answer is unique
README.md defines the two columns, and the question asks for the produce that left the yard, which is the weight with the pallets taken off, so `net_kg` is the column the return needs. Every record's `gross_kg` exceeds its `net_kg` by the same pallet weight, so the two totals differ by the pallets and cannot both be the produce. The decoy 1213200 is the total of the gross column, which includes weight the depot does not dispatch. With the definition applied, the answer is 1134000.

## Fixture notes
Both weight columns are plain integers in kilograms, so either can be totalled directly and the choice between them is the whole question. The journal holds one day, so no date filter narrows the total, and the two bays are interleaved so neither column can be read off one bay alone.
