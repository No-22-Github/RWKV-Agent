## Traps
- None. The index is the only list of what the batch should hold, and one of its four entries has no file.

## Reference solution
1. list_files (1): README.md, accession-index.txt and three scans under scans/.
2. read_file accession-index.txt (2): the index lists scans/3391-basalt.txt, scans/3392-cinder.txt, scans/3393-dolomite.txt and scans/3394-granite.txt, and the folder holds only three scans, so the missing path is scans/3391-basalt.txt.

## Why the answer is unique
The index names four paths and the folder holds exactly three scans, 3392, 3393 and 3394. scans/3391-basalt.txt appears in the index and nowhere on disk, so it is the one path that was never saved. The other three index entries each match a file in scans/ byte for byte in name, and no file in the folder is absent from the index, so exactly one path is missing: scans/3391-basalt.txt.
