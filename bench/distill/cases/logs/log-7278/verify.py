# DISTILL-CANARY-00fdde28 : distillation case
import json
case = json.load(open("case.json"))
app_recs = [json.loads(l) for l in case["files"]["logs/app-2026-09-10.jsonl"].splitlines() if l.strip()]
audit_recs = [json.loads(l) for l in case["files"]["logs/audit-2026-09-10.jsonl"].splitlines() if l.strip()]
app_recs = [json.loads(l) for l in case["files"]["logs/app-2026-09-10.jsonl"].splitlines() if l.strip()]
# Positive control: the log opens with its start-of-day record, so the
# whole window below is covered by the recomputation.
if app_recs[0].get("event") != "service_start":
    raise SystemExit("fixture guard failed: log does not open with service_start")

if audit_recs[0].get("event") != "audit_open":
    raise SystemExit("fixture guard failed: audit log does not open with audit_open")

# The case premise: the member-list export is in neither log, while the
# summary-export decoy lives in the audit log.
for var, recs in (("app", app_recs), ("audit", audit_recs)):
    if any(r.get("event") == "EXPORT_MEMBER_LIST" for r in recs):
        raise SystemExit("fixture records EXPORT_MEMBER_LIST in " + var + "; the absent-event case is broken")
summaries = [r for r in audit_recs if r.get("event") == "EXPORT_SUMMARY"]
if len(summaries) != 2:
    raise SystemExit("fixture guard failed: EXPORT_SUMMARY decoy records are broken")

accepted = ["EXPORT_MEMBER_LIST", "会员名单导出", "member list"]
print(json.dumps({"expected_contains_any": accepted}))
