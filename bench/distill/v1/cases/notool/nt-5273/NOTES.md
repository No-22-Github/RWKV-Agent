## Traps
- TR-NOTOOLNEED: units/dependency-cards.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `Wants=malt-store.service` sits in the card next to the answer: `Wants=` pulls the store in but leaves the drying service free to start when the store fails, which is exactly the failure the crew wants to prevent.

## Reference solution
1. Answer from the service manager: with ordering already given by `After=`, the dependency key that pulls the store in and fails the dependent's start when the store fails is `Requires`, so the line is `Requires=malt-store.service`.
2. Reply with `Requires=malt-store.service`, or one of the accepted spellings `Requires=`, `BindsTo=malt-store.service`, `BindsTo=`.

## Why the answer is unique
The prompt names two behaviours, pulling the store in and staying down when it fails, and gives `After=` so ordering is not part of the question. `Wants=malt-store.service` is not a second reading: it pulls the store in but does not fail the drying service when the store fails. `Requisite=` is not one either: it only checks that the store is already active and never pulls it in, which the prompt rules out. `BindsTo=` is a stronger form of `Requires=` (it also stops the drying service if the store stops later); the prompt does not exclude that extra behaviour, so it is accepted alongside `Requires=`. Scored with output_contains_any over `Requires=malt-store.service`, `Requires=`, `BindsTo=malt-store.service` or `BindsTo=`, which is exactly the row the fixture card records.

## Review 2026-09-29
v1 asked for the key that "refuses to start the drying service while the malt store is not up" and accepted only `Requires=`. Per systemd.unit(5) that wording fits `Requisite=` better (fail immediately if the dependency is not active), and `Requires=` alone gives no ordering without `After=` (verify-shape-review-20260929 flagged it). v2 states `After=` in the prompt, asks for pull-in plus stay-down-on-failure (which rules out `Requisite=`), and also accepts `BindsTo=`. Existing teacher answers `Requires=malt-store.service` (b03 p1/p2, b04 p41) still match; v1.2 rows were rendered from the v1 prompt and are left as they are.
