## Traps
- TR-AMBIG: the first request asks for "the Lamont work", and the September
  register holds two Lamont jobs, LM-31 at Lamont Wharf and LM-22 at Lamont
  Court. Wharf's three invoices total 1277.25; Court's two invoices total 948.75.
  Nothing in the request or the register says which job was meant, so the
  assistant has to ask before adding anything up.

## Reference solution
1. Turn 1: "the Lamont work" names two jobs in the September register, so the
   assistant asks which job is in scope and calls no tool.
2. list_files: the workspace holds invoices/september-jobs.csv and README.md.
3. Turn 2 settles it as Lamont Wharf. read_file the register and add LM-31's
   rows: 412.50 + 268.75 + 596.00 = 1277.25.

## Why the answer is unique
Once the job is fixed, the register has exactly one set of rows for it: LM-31 at
Lamont Wharf with three invoices, each dated in September and each carrying its
own total. Nothing is repeated, no invoice is split across rows, and the README
confirms the amount column is the invoice total. The decoy 948.75 is the true
total of the other Lamont job, LM-22 at Lamont Court, so it answers a different
job rather than a different reading of this one. The invoiced total for Lamont
Wharf is 1277.25.

## Five alternative phrasings of the task
1. tarnside glazing september invoices lamont wharf job
2. invoiced total for job lm-31 lamont wharf
3. lamont court and lamont wharf september invoice register
4. tarnside glazing september job invoices by site
5. how much was invoiced for the lamont wharf job in september
