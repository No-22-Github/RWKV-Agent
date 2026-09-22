<!-- WORKBANK-CANARY-c60b3fa7 : this file must never enter corpora -->

## Traps
- TR-RULEFILE: the pay steps and the night-shift special case live in
  policy.md, not in the question. The data hits the special case exactly:
  RP-4423 (26.0/h, 184.0 h) and RP-4440 (25.2/h, 179.5 h) are on the night
  shift, so all of their hours are paid at 1.25x with no 176-hour step. A
  solver that applies the 176/1.5x step to them as well reports 27854.4
  (registered decoy) instead of 30033.15.
- TR-HEADER: shift_hours_august_2026.csv is a report sheet, not a bare
  table. Three title lines precede the header and the last of them carries
  the period's site accrual, 50594.25; the sheet then closes with
  TOTAL,1781.25, the whole site's hours. A solver that lifts the figure
  printed in the report block reports 50594.25 (registered decoy) instead of
  computing the Moulding figure, 30033.15. The accrual is the whole site's
  pay - the same value the priced Toolroom and Moulding rows sum to - so the
  report block answers a question the prompt did not ask.
  The closing TOTAL line carries no rate and no department, so it prices at
  zero on every path and is not what produces the decoy; it is the other
  half of the same trap (a line that is not a person) and it has to be
  dropped before any per-person join.

## Reference solution
1. read policy.md - 176 h at rate, past 176 at 1.5x, and night shift at
   1.25x for every hour with the step not applying (1)
2. read crew_list.csv - Moulding holds RP-4410, RP-4417, RP-4423, RP-4431,
   RP-4440 and RP-4448, with their rates and shifts (2)
3. read shift_hours_august_2026.csv - the table starts after the three
   report lines, whose accrual figure is the site's and not Moulding's;
   TOTAL is the site figure and is dropped (3)
4. price each Moulding person: 4116.00, 5601.70, 5980.00, 4153.60,
   5654.25, 4527.60 (4)
5. sum: 30033.15 (5)

## Why the answer is unique
Every RP id in the hours sheet appears once in the roster, and the roster
names each person's department, shift and rate, so the Moulding set and its
terms are fixed. policy.md resolves both the step and the special case: for
RP-4423 and RP-4440 the night-shift clause governs, so 5980.00 and 5654.25
are the only figures the stated terms allow. The two decoys are not
alternative readings of this question: 27854.4 applies the step to the night
shift, which policy.md places outside it, and 50594.25 is the whole site's
pay - the accrual the report block prints, Toolroom rows included - whereas
the question names one department. The closing TOTAL line carries neither a
rate nor a department and so prices at zero under the stated terms; it
changes no reading of this question.
