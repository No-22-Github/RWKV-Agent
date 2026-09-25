## Traps
- TR-EARLYHIT: the accreditation scheme's own schedule is the first search
  result and its snippet gives the water sample period (90 days) directly, so one
  search settles the question; the case caps web_search at 1 so a second search
  is scored as a redundant call. The worksheet itself carries no period for water
  samples, only the word PENDING.

## Reference solution
1. list_files: the workspace holds lab/retention-note.txt and README.md.
2. read_file lab/retention-note.txt: the water sample line reads "keep PENDING
   days" and the README says the scheme issues the periods.
3. web_search "wessex scheme water sample retention period": the schedule is the
   first result and its snippet gives 90 days.
4. write_file lab/retention-note.txt with "Water samples: keep 90 days";
   the other three lines stay as they are. Then reply DONE.

## Why the answer is unique
The worksheet holds one pending period and the README points the laboratory at
the scheme for it, so the scheme's current schedule is the only source. Both of
the scheme's pages give 90 days for water samples and the only other figure on
them is the 24 month period that the worksheet already carries for receipts and
printouts, which is a different record type. The pending line is filled in as
"Water samples: keep 90 days".

## Five alternative phrasings of the task
1. wessex scheme retention periods for water samples
2. how long must water samples be held under the wessex scheme
3. wessex accreditation retention schedule laboratory records
4. retention questions water samples 90 days
5. wessex scheme current schedule retention periods
