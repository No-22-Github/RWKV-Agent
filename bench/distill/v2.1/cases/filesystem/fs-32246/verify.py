# DISTILL-CANARY-e1e62590 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '6e00498234a170083ffcc69facf6beceba0dc126be9557bebc67ecacdf9e4441', "fixture changed"
import re
def solve(files):
    rows = sorted((p, len(v.encode())) for p, v in files.items() if p.endswith(".log"))
    out = "path,bytes\n" + "".join("%s,%d\n" % r for r in rows)
    return {"turns": [{"number": len(rows), "items": []}], "files": {"logs/index.csv": out}, "decoys": {}}

ans = solve(case["files"])
print(json.dumps({"files": ans["files"]}, ensure_ascii=False))
