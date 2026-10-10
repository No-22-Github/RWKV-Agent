## Traps
- TR-DECOY: minutes/standup-2026-09-24.txt carries five bullets but only three
  are action items; the foley bullet has no due date and nothing for Mirela to
  do, and the parked bullet explicitly has no owner. Counting bullets gives 5.

## Reference solution
1. Read README.md: follow-up files live in followups/ named YYYY-MM-DD.md and
   list only bullets with an owner and a due date, one line each.
2. Read minutes/standup-2026-09-24.txt.
3. Write followups/2026-09-24.md with the Tomasz, Ines and Dev items.

## Why the answer is unique
An action item needs an owner and a due date, and only Tomasz (due
2026-09-26), Ines (due 2026-09-25) and Dev (due 2026-09-27) have both. The
foley session is booked for October with nothing to do until the studio
confirms the date, and the tide-chart bullet is parked with no owner, so
writing either one as an action item would mean inventing a due date or an
owner that the notes do not carry.
