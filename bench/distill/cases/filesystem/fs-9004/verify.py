# DISTILL-CANARY-f7262d5d : distillation case
import json, re
case = json.load(open("case.json"))
assert case["files"]["inbox/notes.txt"].startswith("Invoices are named inv-YYYY-MM-DD-<seq>.pdf by issue date.")
out = {}
for path, text in case["files"].items():
    m = re.fullmatch(r"inbox/(inv-2026-(\d\d)-\d\d-\d{3}\.pdf)", path)
    if m and int(m.group(2)) <= 6:
        assert text.startswith("%PDF-invoice " + m.group(1)), path
        out["archive/2026H1/" + m.group(1)] = text
print(json.dumps({"files": out}))
