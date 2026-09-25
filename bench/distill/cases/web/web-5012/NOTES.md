## Traps
- TR-EARLYHIT: the first result, rookhaven.example/clients/python/releases, already states the newest Python client default, so one search is enough; rookhaven.example/clients/go/releases is a second page for the Go client where 2000 rows is the newest default and is the decoy.

## Reference solution
1. Search once for the Rookhaven client releases: the first result is the Python client page, whose snippet gives 5000 rows in 5.2.0, and the Go client page is listed with it.
2. Open rookhaven.example/clients/python/releases and confirm that the newest entry, 5.2.0 of 2026-08-28, raises the default batch size to 5000 rows; answer 5000.

## Why the answer is unique
Each page is the release history of one client and the question names the Python client. Its newest entry, 5.2.0, states 5000 rows, while 2000 and 1000 are the defaults of the older Python entries. 2000 is also the newest default of the Go client, which the question does not ask about, and 120 is the query timeout in seconds, not a row count.

## Five alternative phrasings of the task
Every query below carries the fixture keyword rookhaven, so each one is answered by a fixture entry.
1. rookhaven python client releases
2. rookhaven client default batch size
3. rookhaven python client newest release
4. rookhaven batch rows default
5. rookhaven client release notes
