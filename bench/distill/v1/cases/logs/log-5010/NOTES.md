## Traps
- TR-DECOY: the closing line reports rejected=8 and the journal holds eight rejection lines in all, so counting the run's rejections instead of the ones with reason=pack_size_missing gives 8 rather than 5. The other three rejections failed for a missing currency or a price outside the agreed band.

## Reference solution
1. List the workspace: README.md and logs/feed-loader.log.
2. Read README.md: the reason codes are documented, so pack_size_missing is the code for a list that gave no pack size.
3. Read logs/feed-loader.log. Five of the eight rejection lines end in reason=pack_size_missing (PL-3312, PL-3348, PL-3379, PL-3405, PL-3418), so the answer is 5.

## Why the answer is unique
The question asks for one reason code out of the three the loader writes, and README.md ties pack_size_missing to a list that gave no pack size. Five lines carry that code; the other three carry missing_currency or price_out_of_range. The decoy 8 is the run's whole rejection count, and 61 is the count of accepted SKUs, which is not a rejection at all. Counting the lines that carry the asked-for code gives 5.

## Fixture notes
The journal is one run on 12 August 2026 with the closing line accounting for all eight rejections, so no rejection is missing from the file and none is listed twice. The sibling cases in this family use the same journal format, one of them for a question the journal cannot answer.
