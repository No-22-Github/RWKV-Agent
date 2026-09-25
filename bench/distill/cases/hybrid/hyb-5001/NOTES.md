## Traps
- TR-SUPERSEDE: the two search results carry rate cards whose periods do not overlap. The archive copy (freight-archive.example.net) is the February 2026 edition: its own text gives the window 1 February 2026 to 31 May 2026 and records that the carrier withdrew it at the end of May 2026. The carrier's own card (ravensbourne-freight.example/rate-card) is effective 1 June 2026, replaces every earlier card, and has no end date. Billing the September despatches at the February rates (Zone 1 2.95, Zone 2 4.10) gives 3631.50; the rates in force for those despatches (Zone 1 3.20, Zone 2 4.75) give 4105.35.

## Reference solution
1. list_files: the workspace holds depot/despatch-log-2026-09.csv, README.md and notes/depot-handover.txt.
2. read_file depot/despatch-log-2026-09.csv: eight September despatches, Zone 1 rows 240 + 132 + 96 = 468 kg of chargeable weight and Zone 2 rows 118 + 145 + 82 + 130 + 74 = 549 kg.
3. web_search "ravensbourne freight rate card": the February 2026 archive copy and the carrier's own rate card.
4. web_fetch the carrier's rate card: Zone 1 3.20, Zone 2 4.75, effective 1 June 2026. Then 468 x 3.20 = 1497.60 and 549 x 4.75 = 2607.75, so the total is 4105.35.

## Why the answer is unique
The decoy 3631.50 comes from the February 2026 edition, and no despatch in the log can be billed from it: that edition's own text bounds it at 1 February 2026 to 31 May 2026, the archive page states the carrier withdrew it at the end of May 2026, and the carrier's card is effective from 1 June 2026, replaces every earlier card and is open-ended. All eight log rows are dated September 2026, so exactly one rate per zone can apply, and every row carries one of the two zone labels the card prices, so no despatch is left unpriced and no row is repeated. The total is therefore 468 x 3.20 + 549 x 4.75 = 4105.35, a figure that appears in no fixture by itself.

## Five alternative phrasings of the task
1. ravensbourne freight rate card september 2026
2. ravensbourne freight charges per kg by zone
3. ravensbourne freight rates that applied in late 2026
4. ravensbourne freight rate card zone 1 zone 2 prices
5. ravensbourne freight billing rate per kilogram
