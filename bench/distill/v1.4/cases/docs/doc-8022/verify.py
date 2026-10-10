# DISTILL-CANARY-30c5864a : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
report = files["minutes/2026-09-treasurer-report.md"]
assert report.splitlines()[0].startswith("# Treasurer's report")


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("| ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] == "Date":
                continue
            rows.append(cells)
    return rows


head, tail = report.split("## Community grants paid", 1)
rebate_rows = table_rows(head)
grant_rows = table_rows(tail.split("Grants approved after", 1)[0])
assert len(rebate_rows) == 12 and len(grant_rows) == 4
assert max(r[0] for r in grant_rows) == "2026-09-18"
assert "haven't been copied" in report and "backfill" in report
readme = files["minutes/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market minutes")
assert "parish portal" in readme
total = round(sum(float(r[2]) for r in rebate_rows), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
