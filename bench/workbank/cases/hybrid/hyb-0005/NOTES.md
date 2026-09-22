## Traps
- None (L0 baseline). The changelog page and its search snippet both carry the release history, so the kestrelplot version is unambiguous; the getting-started page holds no version at all and is not misleading.

## Reference solution
1. web_search kestrelplot release history (1) - the changelog snippet carries the newest dated entry, 2.1.0 (2026-07-29)
2. read_file service/requirements.txt; the kestrelplot pin is 1.4.2 and the other two pins must survive (2)
3. write_file service/requirements.txt with the kestrelplot pin set to 2.1.0 (3); reply DONE

## Why the answer is unique
The changelog is the only page that carries version numbers, and its entries carry ISO dates, so exactly one entry (2.1.0, 2026-07-29) is the newest. The expected file changes only the kestrelplot pin: contains-checks on all three pins plus unchanged checks on README.md and service/figures.py pin down the edit. The getting-started page mentions no version, so it cannot displace the changelog.

## Five alternative phrasings of the task
1. kestrelplot changelog
2. kestrelplot release history
3. kestrelplot current version
4. kestrelplot library releases
5. kestrelplot package version list

<!-- WORKBANK-CANARY-4f2a91cd : this file must never enter training corpora -->
