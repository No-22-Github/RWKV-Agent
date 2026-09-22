## Traps
- TR-DEFN: "opening-critical" is defined in handbook/premises-handbook.md, section 3, as a check whose recorded consequence of failure is that a building or a service area cannot open; the register (registers/premises-checks.txt) carries that consequence per check. The intuitive reading of the term is by subject matter — the fire, lift, sprinkler and emergency-lighting entries are the conspicuous group and four of the twelve register lines — but three of those four record consequences that stop short of closure (a repair order, an escalated contract, a re-test), so they are not opening-critical. The entries that do qualify include "Kitchen extraction deep clean", whose subject does not sound life-safety at all. A reader who filters on the check names, or who lists the whole register, produces the wrong set; the correct set is Fire alarm weekly test, Kitchen extraction deep clean and Gym equipment safety inspection.
- Grading note: this is a write-file case, so trap_decoys is null per the bank convention (no single wrong value). expect.files checks that the three qualifying names are present; a file that additionally lists the safety-sounding entries that do not qualify is not caught by the automatic scorer and is left to human review.

## Reference solution
1. list_files to see the workspace; the handbook is under handbook/ and the register under registers/ (1)
2. read_file handbook/premises-handbook.md and take the definition of an opening-critical check from section 3 (the consequence of failure decides, not the subject) (2)
3. read_file registers/premises-checks.txt and test every line against that definition (3)
4. write_file reports/opening-critical-checks.md: header "# Opening-critical checks - 2026-08-31" (the export date in the register header) plus the three matching names (4)

## Why the answer is unique
The register is the only list of checks in the workspace and the handbook states that it does not repeat the individual entries, so the candidate set is fixed at twelve. The handbook's definition of opening-critical names one criterion — the recorded consequence of failure is that a building or a service area cannot open — and exactly three register lines carry it ("Fire alarm weekly test", "Kitchen extraction deep clean", "Gym equipment safety inspection"); every other line records a repair order, an escalation, a re-test or a log entry, which the definition excludes. The export date has one source, the register header ("exported 2026-08-31"). verify.py recomputes the set from the register and requires the register header, so deleting that header is detected.

<!-- WORKBANK-CANARY-6f28d1c5 : this file must never enter training corpora -->
