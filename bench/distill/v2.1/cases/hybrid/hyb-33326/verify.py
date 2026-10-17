# DISTILL-CANARY-86346e7b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3f6437a94e0efe7b11377b8bf3cb5ff55f4501a0a1384b78391b233802110d6f', "fixture changed"
def compute(files, web):
    c = {}
    for l in files["inventory/hosts.tsv"].splitlines()[1:]:
        o = l.split("\t")[1]
        c[o] = c.get(o, 0) + 1
    order = sorted(c, key=lambda k: (-c[k], k))
    return {"inventory/os_count.csv": "os,count\n" + "".join("%s,%d\n" % (k, c[k]) for k in order)}, [["%s,%d" % (order[0], c[order[0]])]]

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
