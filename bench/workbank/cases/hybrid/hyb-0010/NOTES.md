## Traps
- TR-DIRMAP: the published tariff table lists "Supply tariff" (0.2735) first and "Offtake tariff" (0.0885) second, with no wording that ties either price to a direction. The mapping lives in operations/settlement-guide.md, which assigns units delivered into the network to the price the network pays for electricity it takes from us — the offtake tariff. Taking the first, larger column gives 48620 x 0.2735 = 13297.57 (decoy).

## Reference solution
1. web_search for Northgate Grid's settlement tariffs (1)
2. web_fetch the tariff page; both prices are per kWh, 0.2735 and 0.0885 (2)
3. read_file operations/settlement-guide.md; deliveries into the network are settled at the price the network pays for units it takes (3)
4. read_file export/monthly.csv; exported volumes sum to 48620 kWh; 48620 x 0.0885 = 4302.87 (4); answer 4302.87

## Why the answer is unique
The portfolio only delivers units into the network — export/monthly.csv records exported kWh with no import column and README.md describes the workspace as export figures — so the guide's second bullet applies and selects one of the two published prices. The guide assigns each direction to exactly one price and the table has exactly two prices, so the mapping is a bijection with no leftover choice. The decoy 13297.57 is wrong concretely: it prices exports at the supply tariff, the price the network charges for electricity it supplies to a site, and Kestrel's sites supplied nothing to themselves. The volumes are whole kWh and the price has four decimals, so the product is exact to the cent.

## Five alternative phrasings of the task
1. northgate grid settlement tariffs
2. northgate grid offtake tariff per kwh
3. northgate grid published electricity tariffs
4. northgate grid tariff rates for generators
5. northgate grid supply and offtake prices

<!-- WORKBANK-CANARY-9c2e5d41 : this file must never enter training corpora -->
