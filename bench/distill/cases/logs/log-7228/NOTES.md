## Traps
- TR-DUPROW: the event bus re-sent 6 nav-fuse ERROR records unchanged, so 27 raw ERROR lines cover 21 distinct events; counting lines overshoots.
- TR-DECOY: 8 ERROR records from path-planner carry 'nav-fuse' inside their detail text, and WARN records from nav-fuse share the component name. Only level=ERROR with component=nav-fuse counts: 21.

## Reference solution
1. Read README.md: record shapes, the re-send rule, and the field test.
2. Search 'nav-fuse' and read the lines around the hits.
3. Keep records with level=ERROR and component=nav-fuse; take the first occurrence of each event_id.
4. The distinct count is 21.

## Why the answer is unique
Re-sent records repeat every field including event_id, so the README's count-once rule makes them one event; detail text is not the component field and WARN is not ERROR. The distinct count is 21.
