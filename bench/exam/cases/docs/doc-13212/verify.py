# EXAM-CANARY-7a7edb58 : exam gap-fill case
import datetime, json, re
case = json.load(open("case.json", encoding="utf-8"))
n = int(re.search(r"Opened software[^:]*: (\d+) days", case["files"]["docs/returns.md"]).group(1))
d = datetime.date(2026, 9, 1) + datetime.timedelta(days=n)
forms = [d.strftime("%b ") + str(d.day), d.strftime("%B ") + str(d.day), d.isoformat(), str(d.day) + d.strftime(" %b"), str(d.day) + "th", d.strftime("%m-%d"), "%d/%d" % (d.month, d.day), str(d.day) + d.strftime(" %B")]
print(json.dumps({"expected_contains_any": forms}))
