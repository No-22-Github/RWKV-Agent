## Traps
- TR-DEFN: the invoice's final column, total_charge, is the all-in figure
  the README names as what the carrier bills, and it is the most visible
  number on each line. The task asks for carriage before the fuel surcharge,
  so the charge comes from base_freight. Taking the all-in totals for the
  five consignments the depot ran gives 329.36 + 110.11 + 136.05 + 1748.98 +
  462.47 = 2786.97 (registered decoy) instead of 2423.45.
- TR-MULTISRC: the invoice lists seven lines but the depot dispatched only
  five - LF-8814 and LF-8847 appear on the carrier invoice and not in
  dispatch_register_july_2026.csv. Summing base_freight over every invoice
  line without checking the register gives 286.40 + 95.75 + 640.20 + 118.30 +
  1520.85 + 73.60 + 402.15 = 3137.25 (registered decoy) instead of 2423.45.
  The other single-source reading runs the join the wrong way: summing the
  register's internal_cost_estimate column gives 2390.30, a plausible but
  equally wrong figure, and it is noted here rather than in trap_decoys
  (one slot per trap).
- Correct figure: base_freight for LF-8801, LF-8809, LF-8822, LF-8835 and
  LF-8859 = 286.40 + 95.75 + 118.30 + 1520.85 + 402.15 = 2423.45.

## Reference solution
1. read_file carrier_invoice_july_2026.csv - seven billed lines, each with
   base_freight and a separate fuel_surcharge (1)
2. read_file dispatch_register_july_2026.csv - the five consignments the
   depot actually ran (2)
3. read_file README.md - base_freight is before the surcharge; the register
   lists what the depot ran (3)
4. keep the five consignments present in both sources and sum their
   base_freight = 2423.45 (4)
5. write_file reports/net_freight.csv with the header 'metric,value' and the
   row net_freight,2423.45 (5)

## Why the answer is unique
The register is the only statement of which consignments the depot ran, so
the join key (consignment_id) fixes the five chargeable lines, and the README
fixes base_freight as the pre-surcharge charge, so both readings collapse to
one sum: 2423.45. LF-8814 and LF-8847 are on the carrier invoice but absent
from the register, so they are excluded by the task's definition rather than
by any judgement call. verify.py recomputes the joined base_freight total
from both files, so corrupting the invoice's header row drops a line and
changes the number, and the sabotage probe is detected.

<!-- WORKBANK-CANARY-e7d0b361 : this file must never enter training corpora -->
