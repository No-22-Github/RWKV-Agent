## Traps
- TR-HEADER: exports/booth-0802.csv opens with two title lines ("Harborview Cinema - projection booth equipment log" and the screen/projector line) and closes with a footer reading "5 events this period". Reading the first line as data or quoting the footer as an answer both mislead; the real fault is the first ERROR row.

## Reference solution
1. Read README.md: column names start on the third line, the footer only counts rows, WARNING rows clear on their own.
2. Read exports/booth-0802.csv, skipping the two title lines and the footer.
3. First ERROR row: 2026-08-01 21:40, code LP-31, laser source current out of range; the fault ends with the INFO row "module replaced under warranty" on 2026-08-02.

## Why the answer is unique
The footer "5 events" counts every row of the export and answers no question about the fault. README fixes the layout (titles take two lines, columns start on the third), so the ERROR rows can only be the 21:40 and 14:12 entries, both code LP-31; the WARNING fan row at 19:05 is advisory and cleared itself, so the fault's first appearance is 21:40. The only "replaced" resolution in the file is the module swap under warranty. Layout, event severity and the resolution row each follow from the fixture's own rules, leaving one reading.
