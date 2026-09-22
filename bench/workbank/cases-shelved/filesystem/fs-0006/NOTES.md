## Traps
- TR-TRUNC: the ingest archive holds 831 files (834 entries counting folders) and every drop file sits at depth 2, but a listing of the workspace root returns at most 500 entries and 200 by default, with a truncation flag set on the result. README.md says the archive is intake/ plus spool/, and the two folders are separated in listing order by manifests/, whose 310 scrolls carry no readings. Any single listing page therefore shows 190 of the 520 drop files: entries 1-200 and entries 1-500 both end inside manifests/. Counting the drop files the tool returned gives 190 (the recorded decoy). A model that does drill into spool/ but leaves the page size alone counts 200 there, since spool/ alone is over the default page, and reports 190 + 200 = 390.

## Reference solution
1. list the workspace root one level deep and see intake/, manifests/ and spool/ (call 1)
2. list intake/ and count its drop files: 190 (call 2)
3. list manifests/ and confirm it holds scrolls only, no readings (call 3)
4. list spool/ and count its drop files: 330; archive total 190 + 330 = 520 (call 4)

## Why the answer is unique
README.md fixes the archive as the union of the open intake folder and the closed spool folder. Every .csv file under those two folders opens with the meter column line and holds exactly one reading, so the set of drop files is unambiguous: 190 in intake/ and 330 in spool/, 520 together. manifests/ holds 310 .txt scrolls and no .csv at all, so including or excluding it moves nothing, and no third folder holds readings. The two folders are disjoint, so no drop is counted twice, and walking the tree at any depth yields the same 520.

<!-- WORKBANK-CANARY-9c1f63a8 : this file must never enter training corpora -->
