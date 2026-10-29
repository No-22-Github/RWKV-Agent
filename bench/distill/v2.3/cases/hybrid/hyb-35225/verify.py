# DISTILL-CANARY-ff2419fb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '11bec3d9477c9025f914b6bb4c2f63634588a63d4583cbf01e10e9336fe44a19', "fixture changed"
EDITS = [["inventory/warehouse-east.csv", "K-204,120", "K-204,80"], ["inventory/warehouse-west.csv", "K-204,55", "K-204,95"]]
ADDS = []
VALS = ["175"]
WRITES = {}
files = dict(case["files"])
final = {}
for path, old, new in EDITS:
    cur = final.get(path, files[path])
    assert cur.count(old) == 1, (path, old)
    final[path] = cur.replace(old, new)
for path, text in ADDS:
    final[path] = final.get(path, files.get(path, "")) + text
for path, subs in WRITES.items():
    final[path] = "\n".join(subs)
pool0 = " ".join(files.values()) + " " + " ".join(t["prompt"] for t in case["turns"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert final[path] == rule["equals"], path
    elif "contains" in rule:
        if path in final:
            assert all(s in final[path] for s in rule["contains"]), path
        else:
            assert path not in files, path
    elif rule.get("unchanged"):
        assert path in files and path not in final, path
pool = " ".join(files.values()) + " " + " ".join(files) + " " + " ".join(final.values()) + " " + " ".join(t["prompt"] for t in case["turns"]) + " " + " ".join(VALS)
for turn in case["turns"]:
    for s in turn["expect"].get("output_contains", []):
        assert s in pool or (s.isdigit() and len(s) <= 3), s
print(json.dumps({"files": final, "answers": [t["expect"].get("output_contains", []) for t in case["turns"]]}, ensure_ascii=False))
