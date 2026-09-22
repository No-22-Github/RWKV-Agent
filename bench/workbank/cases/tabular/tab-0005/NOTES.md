<!-- WORKBANK-CANARY-4b7d9e12 : this file must never enter training corpora -->

## Traps
- None. This is the family's plain base case: a roster and a monthly hours
  log joined on employee_id, one named department summed. Answer 740.5.

## Reference solution
1. read employee_roster.csv - eight people; Outbound holds WX-4821,
   WX-4837, WX-4863, WX-4881 and WX-4902 (1)
2. read hours_log_february_2026.csv - one decimal hours figure per person,
   no preamble and no summary line (2)
3. sum those five figures: 156.5 + 142.0 + 133.75 + 147.5 + 160.75 = 740.5 (3)

## Why the answer is unique
The roster assigns every WX id to exactly one department and the hours log
carries exactly one row per roster id, so the Outbound set is fixed at five
people and each contributes one hours figure. No other hours source exists in
the workspace, and the README states that a person's hours belong to the
department shown beside them in the roster. The obvious near misses -
summing every row regardless of department (1156.0), summing the Ellwood
site's three people (398.25), or summing Outbound at one site only (Ashford
606.75, Ellwood 133.75) - are not defensible readings of a question that
names one department and no site.
