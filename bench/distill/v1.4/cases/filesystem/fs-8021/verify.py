# DISTILL-CANARY-aa507eeb : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
paper = sorted(p for p in files if p.startswith("permits/archive/paper-scans/") and p.endswith(".txt"))
portal = sorted(p for p in files if p.startswith("permits/portal-export/") and p.endswith(".txt"))
assert len(paper) == 41 and len(portal) == 16
for p in paper + portal:
    assert files[p].splitlines()[0] == "Food stall permit"
readme = files["permits/README.md"]
assert readme.splitlines()[0].startswith("# Permit archive")
assert "24 September" in readme and "October batch" in readme
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(len(paper))}))
