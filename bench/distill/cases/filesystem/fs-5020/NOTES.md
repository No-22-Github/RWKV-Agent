## Traps
- TR-DECOY: survey/culvert-13.txt is the sheet for the east barrel of the same lane, drawn on the same day with the same barrel size and the same condition note; only the silt figure, 186 against 180, separates it from culvert 12. A solver who matches the sheets by resemblance rather than by their bytes reports culvert-13.txt, which is the wrong answer.
- TR-MULTISRC: the survey folder alone cannot settle the question. It holds two sheets that read almost the same, and which of them was handed over is only visible in the handover folder, where the copy sits. A solver who reads the survey folder only has to guess between the two.

## Reference solution
1. list_files (1): README.md, handover/culvert-12-review.txt, survey/culvert-12.txt and survey/culvert-13.txt.
2. read_file handover/culvert-12-review.txt (2): the copy kept for the review, silt 180 mm at the inlet, inspection 2026-02-19.
3. read_file survey/culvert-12.txt (3): the same bytes, so this is the sheet that was handed over.
4. read_file survey/culvert-13.txt (4): the east barrel sheet, silt 186 mm, which differs from the copy and is therefore not the one the client asked for.

## Why the answer is unique
The question is which survey sheet is the same document as the copy in the handover folder, so the test is equality of bytes. survey/culvert-13.txt fails that test: its silt line reads 186 mm against the copy's 180 mm, so it is a sheet about a different barrel and cannot be the sheet the client asked for. That leaves survey/culvert-12.txt, which matches the copy line for line. The handover path itself is not an answer to the question, which asks for the sheet as the survey folder writes it, and the survey folder holds exactly two sheets, so only one of them can qualify.
