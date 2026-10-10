# DISTILL-CANARY-93bead2f : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
main = [json.loads(l) for l in files["logs/weighin-main-2026-09.jsonl"].splitlines() if l.strip()]
orch = [json.loads(l) for l in files["logs/weighin-orchard-2026-09.jsonl"].splitlines() if l.strip()]
assert len(main) == 30 and len(orch) == 15
assert {m["date"] for m in main} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {o["date"] for o in orch} == {"2026-09-" + str(d).zfill(2) for d in range(1, 16)}
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market weigh-in logs")
assert "haven't been synced" in readme and "backfill" in readme
total = sum(m["kg"] for m in main)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
