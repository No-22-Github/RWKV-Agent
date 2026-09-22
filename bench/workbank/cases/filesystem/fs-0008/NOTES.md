## Traps
- TR-TRUNC: the archive holds 558 files (575 directory entries), 555 of them three components deep under surveys/<arena>/, and every arena folder is walked before registry/. A recursive listing of the workspace root therefore runs out at both page sizes a listing allows: the 200-entry default stops inside surveys/arena-05/ (last entry surveys/arena-05/hx05-012.tsv) and the 500-entry maximum stops inside surveys/arena-11/ (last entry surveys/arena-11/hx11-036.tsv), each flagging that it stopped early, and neither reaches surveys/registry/. The biggest file either page shows is surveys/arena-01/series_summary.tsv at 3405 bytes, because that summary sorts last inside the first arena folder and everything else a page reaches is a tiny plot sheet. Answering from the page gives 3405 (the recorded decoy). The registry export is 3618.
- TR-DECOY: the compiled series is also written to transfers/registry/compiled_series.csv when a release goes to the national data centre, so the same file name and the same folder shape appear twice in the tree, and the staged copy is the bigger of the two at 4625 bytes. README.md records that staging copies are working files and not part of the archive. A model that ranks every file in the workspace, or that reads the first matching name a listing offers, answers 4625.

## Reference solution
1. list the workspace root one level deep: surveys/, transfers/, notes/ and README.md (call 1)
2. list surveys/ one level: twelve arena folders and registry/ (call 2)
3. list surveys/registry/: the compiled series is 3618 bytes (call 3)
4. list surveys/arena-01/: 46 plot sheets around 25 bytes each and the series summary at 3405 bytes, the biggest thing in any arena folder (call 4)
5. list transfers/registry/ and confirm the staged copy is 4625 bytes but sits outside the archive; answer 3618 (call 5)

## Why the answer is unique
README.md fixes the archive as surveys/ alone, so the staged copy under transfers/ is outside the scope the question names, bigger though it is. Inside surveys/ the sizes are unambiguous: the registry export is 3618 bytes, the arena-01 summary is 3405, and the remaining 552 plot sheets are each under 40 bytes, so there is no tie for the top. The registry folder holds exactly one export, the twelve arena folders hold only plot sheets besides that one summary, and walking the tree at any depth yields the same set of files, so the biggest in-scope file is 3618 bytes however the tree is traversed.

<!-- WORKBANK-CANARY-e63b91c7 : this file must never enter training corpora -->
