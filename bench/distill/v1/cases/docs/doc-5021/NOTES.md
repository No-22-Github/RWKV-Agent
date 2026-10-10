## Traps
- TR-SUPERSEDE: two parameter sheets are kept under `procedures/`, issue 3 for work carried out from October 2023 and issue 6 for work carried out from February 2026, which says it replaces every earlier issue. A solver that works from the older sheet, or picks the lower issue number, reports the decoy 3.

## Reference solution
1. List the workspace: `README.md`, the two parameter sheets under `procedures/` and a QA note under `docs/`.
2. Read `procedures/weld-params-2023.md` (issue 3, applying to work carried out on or after 1 October 2023, withdrawn when the next issue took effect) and `procedures/weld-params-2026.md` (issue 6, issued 12 January 2026, applying to work carried out on or after 1 February 2026, replacing every earlier issue from that date).
3. The job is welded in November 2026, which is after 1 February 2026, so the sheet in force is issue 6 with its currents of 175 A and 115 A: 6.

## Why the answer is unique
The decoy 3 is the earlier issue, and the sheet itself records that it was withdrawn when the next issue took effect, so it governs nothing welded after 1 February 2026. The dates are stated in the sheets rather than in their file names, and the two sheets differ on the currents, so a solver that reads the wrong one gets a different answer; the job date falls inside the window of issue 6 alone. The answer is 6.
