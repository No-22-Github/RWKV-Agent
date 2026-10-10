## Traps
- TR-EARLYHIT: the first search result for the unit is the maker's own
  commissioning sheet, and its snippet already carries the interval (900
  seconds). One search answers the question, so a second search is a redundant
  call and the case caps web_search at 1. The settings value is not in the
  workspace: the blank line is the only interval figure the file holds.

## Reference solution
1. list_files: the workspace holds metering/reporting-setup.txt and README.md.
2. read_file metering/reporting-setup.txt: the reporting_interval_seconds line
   has no value, and the README says every setting comes from the maker's sheet.
3. web_search "kelvinside orchard lane reporting interval": the maker's
   commissioning sheet is the first result and its snippet gives 900 seconds.
4. write_file metering/reporting-setup.txt with reporting_interval_seconds=900;
   the other four lines are left as they were. Then reply DONE.

## Why the answer is unique
The workspace holds one setting to fill and no figure for it: the file's value is
blank and the README states that each setting is taken from the maker's sheet,
so the sheet is the only source. The maker's own pages both give 900 seconds for
this unit, and no other interval figure appears on either page, so there is no
second value to choose between. The answer written into the file is
reporting_interval_seconds=900.

## Five alternative phrasings of the task
1. kelvinside analytics orchard lane reporting interval
2. orchard lane telemetry unit commissioning sheet settings
3. what reporting interval does the orchard lane unit class use
4. kelvinside telemetry faq reporting interval seconds
5. orchard lane orl-14 settings file interval
