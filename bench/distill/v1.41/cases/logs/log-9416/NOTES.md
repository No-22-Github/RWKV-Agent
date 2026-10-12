## Traps
- TR-DECOY: exact answer 62; the loose reading (prefix match on campaign and event) gives 128.
- TR-MULTISRC: 4 files; the first file alone gives 15.

## Reference solution
Turn 1: bash: `cat mailstats/*.dat | awk -F';' '$3=="oct-sale" && $4=="click" {print $2}' | sort -u | wc -l` -> 62
Final answer: 62 recipients.

## Why the answer is unique
campaign and event are whole-value columns; addresses are de-duplicated across files. The README (mailstats/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Unique addresses with a click event in oct-sale?
2. Distinct emails where campaign is oct-sale and event is click.
3. Per mailstats/README.md, how many people clicked oct-sale (each once)?
4. How many distinct recipients clicked the oct-sale campaign, bots excluded?
5. Number of different email addresses with a genuine click in oct-sale.
