## Traps
- TR-DECOY: README.md carries a size list recorded when the logs were typed, and by that list brantfell-2026-04.txt at 562 bytes is the biggest. Two logs were extended after they were typed, so the list is behind the folder: brantfell-2026-03.txt has grown to 576 bytes. A solver who reads the list instead of taking the sizes of the files in the folder reports readings/brantfell-2026-04.txt, which is the wrong answer.

## Reference solution
1. list_files (1): README.md at 424 bytes and the three logs under readings/, brantfell-2026-03.txt at 576 bytes, brantfell-2026-04.txt at 562 bytes and brantfell-2026-05.txt at 463 bytes. The largest is brantfell-2026-03.txt, so the path is readings/brantfell-2026-03.txt.

## Why the answer is unique
The folder fixes the sizes, and the listing gives one size per file: 576, 562, 463 and 424 bytes. Those four values are distinct, so exactly one file is the largest, readings/brantfell-2026-03.txt. The list inside README.md is a record of what the logs measured when they were typed, and it says so; the March and May logs were extended after that, which is why the recorded 461 for March is smaller than the 576 the file now takes. Reading the list as the current sizes contradicts the README's own wording, so the file sizes are the only consistent reading and the answer is readings/brantfell-2026-03.txt.
