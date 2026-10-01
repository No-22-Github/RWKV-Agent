## Traps
- TR-DECOY: the morning run failed test_gift_wrap.py and test_shipping_quote.py; those lines sit earlier in the file and belong to the other run.
- TR-CLAIM: the latest run's summary claims failed=0; the README says summaries are written before the failure parser runs, and the body holds one FAILED line in the latest run.

## Reference solution
1. Read README.md: two runs append to one file; the latest run is the last one.
2. Search FAILED and read the line windows around the hits.
3. Assign each FAILED line to its run by the CI RUN banner above it.
4. The latest run's only FAILED case is test_ledger_posting.py::test_unposted_batch; its module is test_ledger_posting.py.

## Why the answer is unique
The banners partition the file into two runs and the latest run holds exactly one FAILED line; the morning failures sit in other modules and the summary claim is disposed of by the README. The module is test_ledger_posting.py.
