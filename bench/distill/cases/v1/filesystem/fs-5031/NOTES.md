## Traps
- TR-DECOY: README.md carries the number of entries each log had when it was bound, and by that list the north shed's log is ahead with 38 entries against the east log's 34. Entries are not space: the north log's entries are shorter, so east-shed.txt takes 324 bytes against its 319. A solver who works from the cover list instead of the sizes of the files in the folder answers 319, which is the wrong figure.

## Reference solution
1. list_files (1): README.md and the three logs under drying/, east-shed.txt at 324 bytes, north-shed.txt at 319 bytes and west-shed.txt at 204 bytes. The fullest is east-shed.txt, so the answer is 324.

## Why the answer is unique
The listing fixes one size per file and the three are different, so exactly one log occupies the most space. The cover list in README.md counts entries rather than space and says as much in its own words; the north log's entries are shorter than the east log's, which is why being ahead on that list still leaves it at 319 bytes, second of the three. So 319 is the size of the north log, not the size of the fullest one. The answer is 324.
