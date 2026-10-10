## Traps
- TR-DECOY: logs/crusher-throughput.jsonl covers two production days and belt B1 runs on both of them, so the 13 B1 loads of 4 August look exactly like the 13 the question asks for. Adding them to the first day's loads gives 6555 instead of 3283.

## Reference solution
1. List the workspace: README.md and logs/crusher-throughput.jsonl.
2. Read README.md: one record per lorry load, `day` is the production day it counts towards, `belt` names the belt and `tonnes` is the weight of stone.
3. Read logs/crusher-throughput.jsonl, or filter it to `belt` = B1 and `day` = 2026-08-03 and total `tonnes`: the 13 loads of that day sum to 3283.

## Why the answer is unique
README.md says the export covers two production days and that each load belongs to the day in its `day` field, so the 4 August loads are outside what was asked for even though they went over the same belt; the plate they carry, B1, is what makes them read like the wanted loads. The 13 loads of 3 August carry 3283 tonnes between them. The decoy 6555 is that sum with the 13 B1 loads of 4 August folded in, and totalling both belts of 3 August gives 5984, which answers a third question. With the day taken literally, the answer is 3283.

## Fixture notes
`tonnes` is a plain integer in every record so the field can be totalled directly; no other field carries a weight. Both days run the same number of loads and the B1 records are spread through each day rather than grouped, so the two days cannot be told apart by position.
