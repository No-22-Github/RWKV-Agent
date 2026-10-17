# DISTILL-CANARY-9c7c01bf : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a51defae949ac69ef1122edfa8b3c97ac841db7e305fafd1a85d712c421d1184', "fixture changed"
def compute(files, web):
    hot = sorted({l.split(",")[0] for l in files["iot/readings.csv"].splitlines()[1:] if int(l.split(",")[2]) > 80})
    return {"iot/alerts.txt": "".join(s + "\n" for s in hot)}, [[str(len(hot))]]

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
