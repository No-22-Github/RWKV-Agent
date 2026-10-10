# DISTILL-CANARY-931703f7 : distillation case
import json
import re

case = json.load(open("case.json"))

def load(path):
    lines = case["files"][path].splitlines()
    close = re.match(r"^=== JOURNAL CLOSE records=(\d+) writer=\S+ ===$", lines[-1] if lines else "")
    if close is None:
        raise SystemExit("fixture guard failed: " + path + " close line is gone")
    if int(close.group(1)) != len(lines) - 2:
        raise SystemExit("fixture guard failed: " + path + " record count does not match the close line")
    if not lines[0].startswith("=== ") or "JOURNAL" not in lines[0]:
        raise SystemExit("fixture guard failed: " + path + " banner is gone")
    err = set()
    for line in lines[1:-1]:
        m = re.search(r" order=(ord-[0-9a-f]+) ", " " + line + " ")
        if " ERROR " in line and m:
            err.add(m.group(1))
    return err

sf = load("logs/storefront-2026-08-27.log")
fw = load("logs/fulfilment-2026-08-27.log")
both = sf & fw
if len(both) != 1:
    raise SystemExit(f"fixture guard failed: expected exactly one two-stage failure, saw {sorted(both)}")
if "ord-70f3c2a1" not in sf or "ord-70f3c2a1" in fw:
    raise SystemExit("fixture guard failed: the storefront-only decoy is gone")
if "ord-b2418e05" not in fw or "ord-b2418e05" in sf:
    raise SystemExit("fixture guard failed: the fulfilment-only order is gone")
print(json.dumps({"expected": next(iter(both))}))
