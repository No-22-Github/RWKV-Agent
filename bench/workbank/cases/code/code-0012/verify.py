# WORKBANK-CANARY-6ae13b2f : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
target = "dispatch/cutoff.py"
shared = "policy/bounds.py"
content = case["files"][target]

# The window bound lives in the platform-owned module; the service module is
# expected to bind it, and the repair has to keep using that shared bound.
if "DEFAULT_DISPATCH_CLOSE_MINUTE" not in case["files"][shared]:
    raise SystemExit("policy/bounds.py no longer publishes DEFAULT_DISPATCH_CLOSE_MINUTE")

binds = re.compile(r"^\s*from\s+policy\.bounds\s+import\s+DEFAULT_DISPATCH_CLOSE_MINUTE\s*$", re.M)
if not binds.search(content):
    raise SystemExit("dispatch/cutoff.py no longer binds the shared close bound")

# Service terms: the closing minute is outside the window, so the repaired
# comparison has to exclude it.
guard = re.compile(r"^(\s*return\s+at_minute\s+)(?:<=|<|>=|>)(\s*DEFAULT_DISPATCH_CLOSE_MINUTE\b)", re.M)
fixed, replaced = guard.subn(r"\g<1><\g<2>", content, count=1)
if replaced != 1:
    raise SystemExit("expected exactly one dispatch-window comparison, matched %d" % replaced)

print(json.dumps({"files": {target: fixed}}))
