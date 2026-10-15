# EXAM-CANARY-e4478a30 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
import datetime as dt
for line in case["files"]["billing/invoices.csv"].splitlines()[1:]:
    iid, _c, d, terms, _a = line.split(",")
    if iid == "INV-2281":
        due = dt.date.fromisoformat(d) + dt.timedelta(days=int(terms.split()[1]))
print(json.dumps({"expected_contains_any": [due.isoformat(), due.strftime("%B ") + str(due.day), due.strftime("%b ") + str(due.day), "%d %s" % (due.day, due.strftime("%B")), "%d %s" % (due.day, due.strftime("%b")), "%d/%d/%d" % (due.month, due.day, due.year), "%d月%d日" % (due.month, due.day)]}))
