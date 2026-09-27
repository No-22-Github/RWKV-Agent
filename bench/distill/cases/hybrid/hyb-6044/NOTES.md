## Traps
- TR-NUMFMT: demurrage prints with a currency symbol and a group separator, so the column cannot be aggregated as numbers. Tallying by eye and dropping the cents gives 176.6 instead of 177.0 for the Felixstowe-Duisburg average.
- TR-MISSING: the route mixes an empty cell, a dash and NA for consignments with no charge. Dividing the recorded sum by all eight consignments gives 110.62 instead of 177.0.

## Reference solution
1. Turn 1: list_files to find the charges file and the README.
2. read README.md: empty, dash and NA mean nothing was charged, and those consignments carry no demurrage.
3. read charges/september-2026.csv; the formatted column errors out in aggregation tools, so the amounts are parsed by hand.
4. average Felixstowe-Duisburg's five charged consignments with the calculator: 884.98 / 5 = 177.0.
5. Turn 2 needs no further call: the same read gives Tilbury-Lyon's four charged consignments, 635.03 / 4 = 158.76.

## Why the answer is unique
The README settles both column behaviours: nothing charged is an empty cell, a dash or NA, and those consignments drop out of any average, leaving five charged values on Felixstowe-Duisburg and four on Tilbury-Lyon. Keeping the printed cents is the only full reading of the amounts; dropping them gives 176.6 and dividing across all eight consignments treats uncharged ones as zeros, neither of which the file supports. So the averages are 177.0 and 158.76.

## Five alternative phrasings of the task
1. quaymont brokerage felixstowe duisburg demurrage average
2. tilbury lyon demurrage per consignment
3. quaymont september demurrage by route
4. average demurrage charge quaymont 2026
5. quaymont deep sea route charges september
