## Traps
- TR-RULEFILE: the per-consignment charge comes from finance/carriage-rates-2026.md, whose final clause moves everything over 90 kg onto a flat 58.40 pallet-network rate. Rating C-2241 (112.4 kg, Regional) at the zone price instead gives 148.37.

## Reference solution
1. Turn 1: list_files to find the shipment list and the rate card.
2. read finance/carriage-rates-2026.md: zone prices per kg, and everything over 90 kg rides the pallet network at a flat 58.40.
3. read shipments/may-2026.csv; C-2241 weighs 112.4 kg, above the flat-rate threshold, so its charge is 58.40.
4. Turn 2 needs no further call: the rate card and the shipment row for C-2247 (76.2 kg, Highland) were both read in turn 1, giving 76.2 x 2.05 = 156.21.

## Why the answer is unique
The rate card is the only place the charges are defined, and its final clause takes every consignment over 90 kg off the per-kg prices: C-2241 at 112.4 kg is a flat 58.40, and the 148.37 reading applies a price the carrier explicitly does not use for that weight. C-2247 at 76.2 kg stays under the threshold, so its Highland per-kg price applies and 76.2 x 2.05 = 156.21. No other rate appears in the card.

## Five alternative phrasings of the task
1. thorness joinery carriage charge c-2241
2. may consignment charges thorness joinery
3. what did c-2247 cost to send
4. thorness pallet network flat rate
5. thorness joinery shipping may 2026
