## Traps
- TR-MULTISRC: booking-only failures (shp-a6d6cf83, shp-0e7fbeb1, shp-20d56c03) and dispatch-only failures (shp-d6d4e002, shp-df53acec, shp-8e13bf7d) each look decisive inside one journal, and shp-6c8a07dc carries only a booking WARN next to its dispatch ERROR. A shipment counts only when its reference appears as an ERROR in the two journals; that intersection holds exactly shp-1c559e6b.

## Reference solution
1. Read README.md: the two journals, the shipment field, and that a line belongs to the shipment named in it.
2. Search ERROR lines in logs/booking-2026-05-19.log and collect their shipment references.
3. Search ERROR lines in logs/dispatch-2026-05-19.log and collect theirs.
4. Intersect the two sets; the WARN pairing of shp-6c8a07dc stays out because a WARN is not an ERROR.
5. The single common reference is shp-1c559e6b.

## Why the answer is unique
The README pins the shipment field as the join key, and the journals name their writing service on every line, so the intersection is well defined. WARN lines are excluded by level, and every other reference fails in only one stage. The intersection holds exactly one reference: shp-1c559e6b.
