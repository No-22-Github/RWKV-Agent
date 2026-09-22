<!-- WORKBANK-CANARY-a93c2f60 : this file must never enter training corpora -->

## Traps
- TR-HEADER: hours_april_2026.csv is a report sheet, not a bare table. The
  header sits on the fourth line (three title lines precede it) and the last
  line is TOTAL,1840.0, the whole sheet's figure across every department. The
  question asks for one department, Grounds. A solver that reads the sheet's
  own closing figure as the department's answer reports 1840.0 (registered
  decoy) instead of 906.75; a solver that sums the column without dropping
  the TOTAL line doubles the sheet total to 3680.0, and neither is the
  Grounds figure.
  Attribution caveat: 1840.0 is reachable two ways - lifting the TOTAL line,
  and summing every person row without filtering by department - because a
  consistent total line restates its own column. An answer of 1840.0 is
  therefore not proof on its own that the total line was the cause, and a
  trap-level tally that counts it as a TR-HEADER hit is counting a
  department-scope error alongside it. 3680.0 is the only value on this case
  that the total line alone can produce.

## Reference solution
1. read employee_roster.csv - twelve people; Grounds holds WC-2081,
   WC-2094, WC-2103, WC-2117, WC-2126 and WC-2138 (1)
2. read hours_april_2026.csv - the table starts after the three report
   lines; the closing TOTAL line is the whole sheet, not a person (2)
3. match each hours row to a Grounds roster row and drop TOTAL (3)
4. sum: 141.25 + 158.75 + 149.5 + 137.0 + 153.5 + 166.75 = 906.75 (4)

## Why the answer is unique
The roster gives every WC id exactly one department, the hours sheet gives
every roster id exactly one figure, and the README states that a person's
hours belong to the department shown beside them in the roster. So the
Grounds set is fixed at six people and the sum is 906.75. The TOTAL line is
not a candidate reading: it carries no employee id that appears in the
roster, and the question names one department, so neither the sheet-wide
1840.0 nor the doubled 3680.0 answers it.
