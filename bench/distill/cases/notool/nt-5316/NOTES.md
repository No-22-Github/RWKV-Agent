## Traps
- TR-AMBIG: the first message asks for the haulage price on a full load without saying which site it goes to. The zone list carries three sites (Barrowfield Yard in zone B, Corranhead Works in zone A, Larkwell Quarry in zone C) and the rate card prices each zone, and nothing in the workspace says where Thursday's load is tipped, so a first turn that quotes a figure has guessed; the correct first turn is a question with no tool call. The second turn names Corranhead Works and the answer is the zone A price of 210.00. The careless answer is 372.50, the zone B price that the first site on the list carries.

## Reference solution
1. Turn 1: ask which site the load goes to, since the zone and the price follow it; no calls.
2. Turn 2 (Corranhead Works named): read sites/site-zones.csv for the zone (A) and rates/zone-rates-2026-09.csv for the price of a full load into zone A, which is 210.00, a total of 2 calls.

## Why the answer is unique
Once the site is named the zone follows from the site list and one row of the rate card is left: a full load into zone A costs 210.00. The decoy 372.50 is the zone B price, and zone B is Barrowfield Yard, so it cannot answer a load going to Corranhead Works. Nothing in the workspace says where the Thursday gravel goes, so the choice belongs to the requester and no reading of the files settles it before the second turn.
