## Traps
No traps. One search returns the release notes and the first line of the changes
block gives the shard count.

## Reference solution
1. Search for the Harrowden Tools exporter release; the only result is
   harrowden-tools.example/releases/exporter-3-4.
2. Open the notes: 3.4 is the current release and a run spreads over 12 shards.

## Why the answer is unique
The page is written by the tool's own maintainers for the release it announces, and
the question asks about the current release, so the figure that applies is the one
3.4 ships. 8 is the previous release's figure, named on the same page as the value
3.4 replaced, and the notes say the shards key stays optional, so a configuration
that leaves it unset takes the shipped figure rather than the older one.

## Five alternative phrasings of the task
1. harrowden tools exporter release notes shards
2. harrowden exporter current release default shard count
3. how many shards does a harrowden exporter run use
4. harrowden tools exporter 3.4 shipped defaults
5. harrowden exporter parallel upload shards
