## Traps
- TR-SUPERSEDE: policy/vendor-circular-52.md (issued 14 October 2025) is replaced by policy/vendor-circular-31.md (issued 2 June 2026, effective 1 July 2026). Issue dates live only in the document titles and the numbering misleads (52 > 31 although 31 is the newer issue). A model that transcribes circular 52's steps produces "Sign-off from the procurement lead", "EUR 1,000,000" and the faxed questionnaire instead of the required "dual sign-off" and "EUR 2,000,000" items, and its header date would be 2025-10-14 instead of 2026-06-02.
- TR-MULTISRC: the current requirements span two sources - circular 31 (three steps) and the 19 August 2026 review minutes (the agreed signed-NDA requirement). Working only from the circulars omits "signed NDA"; working only from the minutes omits the policy steps. Each source alone yields a plausible but incomplete checklist.
- Grading note: this is a write-file case, so both trap_decoys are null per the bank convention (no single wrong value). expect.files checks presence of the required items; a checklist that ALSO lists withdrawn items is not caught by the automatic scorer and is left to human review.
## Reference solution
1. list_files (1)
2. read_file policy/vendor-circular-31.md (2)
3. read_file policy/vendor-circular-52.md (3)
4. read_file vendor-review-minutes-2026-08-19.md (4)
5. write_file ops/checklist.md: header with 2026-06-02 plus the three circular-31 steps and the signed-NDA requirement (5)
## Why the answer is unique
Circular 31 explicitly replaces circular 52, so exactly one circular is in force on the fixed clock (2026-09-16); the minutes confirm this and add exactly one agreed onboarding requirement, while their two Action lines are one-off tasks rather than onboarding requirements. The prompt pins the header to the issue date of the governing circular and requires the source wording, so every contains substring is determined. verify.py recomputes the checklist from circular 31 and the minutes and takes the header date from circular 31's title line, so corrupting that line is detected (verify exits non-zero).

<!-- WORKBANK-CANARY-2b8f60d3 : this file must never enter training corpora -->
