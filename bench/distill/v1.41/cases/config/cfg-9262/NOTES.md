## Traps
- TR-READONLY: config/example.env is the template and stays; API_BASE_LEGACY=https://api-v1.corp.io is a look-alike line (a global `s/api-v1/api-v2/` changes it).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find config -name '*.env' | grep -v example.env | xargs sed -i 's#^API_BASE=https://api-v1\.corp\.io$#API_BASE=https://api-v2.corp.io#'`
2. bash: `grep -rn '^API_BASE=' config`
Final answer: DONE (web, mobile, billing, admin, jobs on api-v2).
Turn 2:
1. bash: `sed -i 's#^API_BASE=.*$#API_BASE=https://api-v1.corp.io#' config/billing.env && sed -i 's#^API_BASE=.*$#API_BASE=https://api-v2-eu.corp.io#' config/jobs.env`
2. bash: `grep -rn '^API_BASE=' config`
Final answer: DONE (billing on v1, jobs on api-v2-eu, the rest on v2).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. Switch API_BASE to api-v2 in all services except the template, then billing goes back to v1 and jobs gets the EU host.
2. Move every service to the v2 API (not the legacy key), afterwards undo billing and give jobs api-v2-eu.
3. api-v1 to api-v2 for API_BASE everywhere except example.env; then billing reverts and jobs uses api-v2-eu.corp.io.
4. Update API_BASE for the services, then billing stays on the old API and jobs on the EU one.
5. 把各服务的 API_BASE 改到 v2，之后 billing 改回 v1、jobs 改成 EU 地址
