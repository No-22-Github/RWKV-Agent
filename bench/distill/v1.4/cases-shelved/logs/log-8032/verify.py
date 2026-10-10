# DISTILL-CANARY-63210a62 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
term = [json.loads(l) for l in files["logs/terminal-bank-2026-09.jsonl"].splitlines() if l.strip()]
roam = [json.loads(l) for l in files["logs/roaming-reader-2026-09.jsonl"].splitlines() if l.strip()]
days9 = ["2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12", "2026-09-15",
         "2026-09-19", "2026-09-22", "2026-09-26", "2026-09-29"]
assert len(term) == 18 and {(t["date"], t["terminal"]) for t in term} == {
    (d, t) for d in days9 for t in ("T1", "T2")}
assert len(roam) == 5 and {r["date"] for r in roam} == set(days9[:5])
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market card terminal logs")
assert "haven't been exported" in readme and "first export" in readme
total = sum(t["approved"] + t["declined"] for t in term)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
