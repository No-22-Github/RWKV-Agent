## Traps
- TR-RULEFILE: the body of handbook/field-operations-handbook.md gives the general priority 2 acknowledgement target, 45 minutes, in section 3; the site-specific value lives in a second document, handbook/appendix-c-upland-worksites.md, whose C.2 sets 75 minutes for the three unmanned upland sites and states that its value governs where it differs. The question names Tarnbeck reservoir, one of the three. A reader who stops at the handbook answers 45 minutes, the decoy; the applicable figure is 75.

## Reference solution
1. list_files to see the workspace layout; the handbook and its appendix are under handbook/ (1)
2. read_file handbook/field-operations-handbook.md and note the section 3 target for priority 2 jobs: 45 minutes (2)
3. read_file handbook/appendix-c-upland-worksites.md; C.1 lists Tarnbeck reservoir and C.2 sets 75 minutes for priority 2 jobs at the sites in C.1, governing over the body of the handbook (3)
4. Report the applicable figure for that site: 75 (4)

## Why the answer is unique
The workspace holds exactly one handbook and one appendix, and the appendix states both its scope (the three sites in its C.1 table, Tarnbeck reservoir among them) and its precedence over the body of the handbook, so a priority 2 job at Tarnbeck reservoir is governed by one value only. The 45-minute figure in section 3 is the general target and applies to every other site; it cannot apply here because the appendix changes it for exactly this class of site. verify.py parses the general target from the handbook and the override from the appendix and refuses a fixture where the appendix does not override, so corrupting the 75 is detected.

<!-- WORKBANK-CANARY-e9b3a742 : this file must never enter training corpora -->
