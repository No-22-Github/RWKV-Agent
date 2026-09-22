# WORKBANK-CANARY-9b2e7d61 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
target = "billing/notices.py"
content = case["files"][target]

# The declared notice floor is part of the module contract; without it the
# notice terms the repair has to satisfy are no longer stated anywhere.
floor = re.compile(r"^\s*FREE_NOTICE_DAYS\s*=\s*14\b", re.M)
if not floor.search(content):
    raise SystemExit("billing/notices.py no longer declares FREE_NOTICE_DAYS = 14")

# Desk terms: free only with notice of more than FREE_NOTICE_DAYS days, so
# the repaired guard has to exclude the boundary day itself.
guard = re.compile(r"^(\s*if\s+notice_days\s+)(?:>=|<=|>|<)(\s*FREE_NOTICE_DAYS:)", re.M)
fixed, replaced = guard.subn(r"\g<1>>\g<2>", content)
if replaced != 1:
    raise SystemExit("expected exactly one notice guard, matched %d" % replaced)

print(json.dumps({"files": {target: fixed}}))
