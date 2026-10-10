# DISTILL-CANARY-4f620967 : distillation case
import json

case = json.load(open("case.json"))
files = dict(case["files"])
files.update(case["expect"]["run"]["hidden_files"])

days = {}
for path in sorted(files):
    if not path.endswith(".json"):
        continue
    export = json.loads(files[path])
    for sale in export["sales"]:
        day = sale["sold_at"][:10]
        count, pence = days.get(day, (0, 0))
        days[day] = (count + 1, pence + sale["pence"])

lines = []
sales = 0
pence = 0
for day in sorted(days):
    count, takings = days[day]
    sales += count
    pence += takings
    lines.append("%s,%d,%d" % (day, count, takings))
lines.append("TOTAL,%d,%d" % (sales, pence))

keep = "tills/2026-09.json"
print(json.dumps({
    "expected_stdout": "\n".join(lines),
    "files": {keep: files[keep]},
}))
