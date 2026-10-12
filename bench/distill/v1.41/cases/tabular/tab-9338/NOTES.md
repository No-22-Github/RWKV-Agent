## Traps
- TR-DECOY: exact answer yard; the loose reading (device prefix match, includes bot-AB) gives hall-east. Several rows share the extreme value; file order would give hall-east, the README rule gives yard.
- TR-TRUNC: the file is 76KB and 1308 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F';' '$2=="bot-A" {print $3, $1, $4}' fleet/battery.txt | sort -k1,1n -k2,2 | head -1` -> yard
        then `awk -F';' '$2=="bot-A"' fleet/battery.txt | wc -l` for the row count asked in the prompt (551)
Final answer: bot-A was at yard when its battery was lowest; bot-A has 551 samples in total.

## Why the answer is unique
device is a whole-value column; the lowest level is shared by several rows and the README picks the earliest ts. The README (fleet/README.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. Where was bot-A when its battery hit the lowest level? Earliest sample wins ties.
2. Site of bot-A's lowest battery sample in battery.txt, per the README tie rule.
3. Which site did bot-A report from at its minimum battery_pct?
4. Find bot-A's lowest battery reading and tell me the site (earliest ts if tied).
5. At minimum charge, which site was robot bot-A at?
