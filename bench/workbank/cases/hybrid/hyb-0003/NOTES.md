## Traps
- TR-SUPERSEDE: the 3.4.0 announcement post (published 2026-02-11) ranks first in search and carries the most eye-catching version number, while the changelog page lists 3.6.2 dated 2026-08-18 above 3.4.0 dated 2026-02-11. Pinning the announcement's 3.4.0 is the decoy.

## Reference solution
1. web_search farebook changelog (1)
2. web_fetch the changelog page; the newest dated entry is 3.6.2 (2026-08-18), which supersedes the announcement's 3.4.0 (2)
3. read_file service/requirements.txt (3)
4. write_file service/requirements.txt with the farebook pin set to 3.6.2 and the other two pins untouched (4); reply DONE

## Why the answer is unique
Only one changelog exists and its entries carry ISO dates, so exactly one entry (3.6.2) is the current release. The expected file changes only the farebook pin; contains-checks on all three pins plus unchanged checks on README.md and service/booking_api.py pin down the edit.

## Five alternative phrasings of the task
1. farebook changelog
2. farebook python library releases
3. farebook current version
4. farebook project release notes
5. farebook library version history
