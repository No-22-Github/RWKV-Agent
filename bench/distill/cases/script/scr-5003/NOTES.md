## Traps
- None. No trap tag is set: the sheet's layout and its date order are stated in the module notes of the script that prints it, and the script itself does not follow that order.

## Reference solution
1. Read tally.py: its module notes say one line per session in date order, while main() walks the rows as they come out of session_rows() (call 1).
2. Sort those rows by their date before printing them (call 2), leaving the export under sessions/ and the totals line as they are.

## Why the answer is unique
The export lists a month's sessions in booking order, not in date order, so the sheet depends on the sort and on nothing else: each row is printed with the date and the attendee count it carries, and the totals line sums those counts. With both monthly exports in place the repaired script prints:

    2026-09-01,18
    2026-09-02,27
    2026-09-03,21
    2026-09-04,32
    2026-10-01,36
    2026-10-02,24
    2026-10-05,19
    TOTAL,177

Sorting the export in place instead of the rows in the script cannot be the repair: the October export arrives after the repair and carries its own order, and sessions/ is the tablet's record.

