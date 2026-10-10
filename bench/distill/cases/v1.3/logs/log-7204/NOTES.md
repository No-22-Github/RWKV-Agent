## Traps
- TR-MULTISRC: the evening produced single-stage failures that each look like the answer if one journal is read alone. ord-70f3c2a1 was declined at checkout (2026-08-27T19:02:52.787Z, then cancelled) and never reached the warehouse; ord-b2418e05 jammed a label printer in fulfilment (2026-08-27T19:34:33.154Z) and printed on retry; three more storefront ERRORs (ord-e3a17c22, ord-f7b29d10, ord-a5c83e66) never left checkout either. Only ord-c91d40b7 has an ERROR in both journals (2026-08-27T23:21:50.890Z storefront, 2026-08-27T23:47:21.956Z fulfilment).

## Reference solution
1. Read README.md: two stages, order= on every line, and the rule that an end-to-end failure shows an ERROR in both journals.
2. Collect the ERROR order references in logs/storefront-2026-08-27.log.
3. Collect the ERROR order references in logs/fulfilment-2026-08-27.log.
4. Intersect the two sets and check the single-stage failures against the README's decline/cancel and retry/recovery patterns.
5. The only order with an ERROR in both journals is ord-c91d40b7.

## Why the answer is unique
The README states the pipeline semantics: a declined checkout never reaches the warehouse, and a recovered warehouse fault carries a recovery line, so the single-stage failures are excluded by the record pattern itself, not by taste. The ERROR-order sets of the two journals intersect in exactly one reference, ord-c91d40b7, and each journal pins its own line count in the CLOSE record, so neither file can be read partially without noticing. The answer is ord-c91d40b7.
