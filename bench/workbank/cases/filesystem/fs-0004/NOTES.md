## Traps
- TR-DECOY: assets/icons/weather_squall.svg and assets/seasonal/weather_squall.svg share their file name in two folders, but their bytes differ (stroke and dot colour #3b6ea5 vs #7a4fa3, dot radius 3 vs 4). A model that matches duplication by name instead of content reports weather_squall.svg (the recorded decoy). Only the cairn badge pair is byte-identical.
- TR-NEARNAME: README.md says earlier builds shipped the badge as cairn-badge.svg (hyphen). That name is not on disk. The duplicated file's real name is cairn_badge.svg (underscore); answering cairn-badge.svg from the prose is the recorded decoy.

## Reference solution
1. list_files the workspace and collect the nine .svg entries under assets/ (call 1)
2. read assets/logos/cairn_badge.svg (call 2)
3. read assets/archive/cairn_badge.svg and confirm the bytes are identical (call 3)
4. read assets/icons/weather_squall.svg (call 4)
5. read assets/seasonal/weather_squall.svg and confirm the bytes differ (call 5)
6. tally the .svg count from the listing and answer: 9 files, duplicated file cairn_badge.svg (call 6)

## Why the answer is unique
Grouping all nine .svg files under assets/ by exact content leaves exactly one group with two members (the two cairn_badge.svg copies). The squall pair differs in bytes, every other glyph appears once, and the count of .svg file entries is fixed at nine regardless of how the tree is walked.

<!-- WORKBANK-CANARY-e2f83b56 : this file must never enter training corpora -->
