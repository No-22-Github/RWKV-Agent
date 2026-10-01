# DISTILL-CANARY-1a271ef2 : distillation case
import hashlib
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
target = "财务共享盘/总表.csv"
h = hashlib.md5(files[target].encode("utf-8")).hexdigest()
dups = sorted(
    p for p in files
    if p != target and p.endswith(".csv") and hashlib.md5(files[p].encode("utf-8")).hexdigest() == h
)
if len(dups) != 1:
    raise SystemExit("expected exactly one identical copy, found %d: %r" % (len(dups), dups))
print(json.dumps({"expected_string": dups[0]}, ensure_ascii=False))
