## Traps
- TR-DECOY: the closing line reports rejected=6 and the journal holds six rejection lines in all, so counting the run's rejections instead of the ones with reason=missing_currency gives 6 rather than 4. The other two rejections failed for a missing pack size or a price outside the agreed band.

## Reference solution
1. List the workspace: README.md and logs/feed-loader.log.
2. Read README.md: the reason codes are documented, so missing_currency is the code for a price quoted with no currency.
3. Read logs/feed-loader.log. Four of the six rejection lines end in reason=missing_currency (HD-2204, HD-2231, HD-2259, HD-2266), so the answer is 4.

## Why the answer is unique
The question asks for one reason code out of the three the loader writes, and README.md ties missing_currency to a price quoted with no currency. Four lines carry that code, and the remaining two carry pack_size_missing or price_out_of_range. The decoy 6 is the run's whole rejection count and 38 is the count of accepted SKUs, which is not a rejection at all. Counting the lines that carry the asked-for code gives 4.

## Fixture notes
The journal is one run on 4 September 2026 with the closing line accounting for all six rejections, so no rejection is missing from the file and none is listed twice. The sibling cases in this family use the same journal format, one of them for a question the journal cannot answer.
