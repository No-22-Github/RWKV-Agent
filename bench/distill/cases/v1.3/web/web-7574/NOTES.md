## Traps
- TR-FETCHFAIL: the status history page ranks first but its fetch fails with a 502 provider error, so the answer has to come from the vendor migration page instead of giving up.
- TR-WEBSTALE: the April summary on payrollradar still reports the original 2026-09-15 retirement; the vendor migration page (updated 2026-08-28) says the sunset is extended to 2026-11-15.

## Reference solution
1. web_search pellbridge v2 payroll api keys stop working date
2. web_fetch status.pellbridge.example/history; the extract fails with a 502 provider error
3. web_fetch www.pellbridge.example/docs/v2-migration; the sunset is extended to 2026-11-15
4. Answer 2026-11-15.

## Why the answer is unique
The vendor migration page, updated 2026-08-28, states the sunset is extended to 2026-11-15 and that v2 keys stop working after that date. The April summary's 2026-09-15 is the original plan from before the extension and payrollradar's own post is dated four months earlier than the notice, so it cannot describe the current cut-off; the failed status page offers no value at all. 2026-11-15 is the only supportable answer.

## Five alternative phrasings of the task
1. pellbridge v2 payroll api keys stop working
2. pellbridge v2 sunset extended date
3. pellbridge payroll v2 migration cut-off
4. pellbridge v2 payroll api retire 2026-11-15
5. pellbridge migration page v2 keys
