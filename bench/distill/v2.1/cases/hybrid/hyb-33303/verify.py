# DISTILL-CANARY-9b14d608 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '51d0c9548cc97ab0dc2ea2af8ba1d29ff8ef6b97ae3618d0cadd1b1c878c3c14', "fixture changed"
def compute(files, web):
    pg = [w for w in web if "cobaltmail" in w["url"]][0]["content"]
    s = pg.split("Start: ")[1].split("\n")[0]
    e = pg.split("End: ")[1].split("\n")[0]
    t = files["ops/calendar.md"].replace("Cobalt Mail maintenance: TBD", "Cobalt Mail maintenance: %s to %s" % (s, e))
    return {"ops/calendar.md": t}, [[s, e]]

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
