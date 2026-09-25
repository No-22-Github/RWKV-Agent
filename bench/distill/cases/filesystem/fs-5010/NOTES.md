## Traps
- TR-SUPERSEDE: checklists/checklist-rev4.txt names revision 3 as the revision it replaces, so revision 3 is the older copy and its "every 14 days" line is out of date. Running the inspection on the older interval gives 14.
- TR-DECOY: revision 3 is the near-identical companion file; it differs from revision 4 only in the issue line, the supersede line, the frequency and one item per check.

## Reference solution
1. list_files (1): README.md and two checklists under checklists/.
2. read_file checklists/checklist-rev3.txt (2): revision 3, issued 2026-05-18, replacing revision 2, frequency every 14 days.
3. read_file checklists/checklist-rev4.txt (3): revision 4, issued 2026-08-03, replacing revision 3.
4. The copy that replaces the older one is revision 4, whose frequency line reads "Frequency: every 7 days", so 7 days may pass between inspections (4).

## Why the answer is unique
Only revision 4 names a revision that is present in the folder as the one it replaces, which makes it the copy in force; revision 3 replaces revision 2, which is not in the folder. The interval therefore comes from revision 4 alone, and its frequency line states one figure, 7 days. The 14 days in revision 3 belongs to the replaced copy, so it is the answer only for a reader who takes the older revision as current.
