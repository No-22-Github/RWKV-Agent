## Traps
- TR-DECOY: Cascadia and Modern Art appear in both stock/manifest-north.csv and stock/manifest-south.csv. Adding the two manifests line by line reports 7 titles; README says a title in both rooms is one collection split across rooms and counts once, so the cafe holds 5.

## Reference solution
1. List the stock folder: two manifests, north and south.
2. Read README.md: a title shelved in both rooms is one collection split across rooms.
3. Read both manifests: union of titles is Azul Summer Pavilion, Cascadia, Heat Pedal to the Metal, Modern Art, Wingspan = 5; the overlap is Cascadia and Modern Art.


> v2（2026-10-01）：判据改写——output_contains 只留专有名词事实，数量事实移入 output_contains_any 并给多种自然写法（原「数字+量词」锚串对自然语言终答过严）。

## Why the answer is unique
The decoy 7 titles counts the two shared titles once per room. README defines a title in both manifests as one collection split across rooms and says counts quote each title once, so the union can only be 5. The intersection is exactly the title set appearing in both files, Cascadia and Modern Art, and no third title occurs twice. The counting rule and the per-room rows fix all three facts, leaving no second reading.
