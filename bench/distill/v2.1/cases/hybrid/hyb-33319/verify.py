# DISTILL-CANARY-ac329148 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ec27554bd94d6a992ee1a5057d06b8a58fa5642cb1c8dde27e37d767d0e93b87', "fixture changed"
def compute(files, web):
    out = []
    for l in files["仓库/库存.csv"].splitlines()[1:]:
        a = l.split(",")
        if int(a[2]) < int(a[3]):
            out.append(a[0])
    return {"仓库/补货清单.txt": "".join(s + "\n" for s in out)}, [[str(len(out))]]

FINAL, ANS = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
for turn, a in zip(case["turns"], ANS):
    e = turn["expect"]
    assert set(a) <= set(e.get("output_contains", [])) | set(e.get("output_contains_any", [])), a
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}, "answers": ANS}, ensure_ascii=False))
