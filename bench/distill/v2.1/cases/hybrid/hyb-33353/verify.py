# DISTILL-CANARY-7032f5c1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'fe0039e8f92616325bcc1666d7009429f231189c14ace8fcc90bc1ea9600a7b8', "fixture changed"
def compute(files, web):
    import re
    p = re.search(r"listen_port=(\d+)", files["部署/a.cfg"]).group(1)
    h = re.search(r"host=(\S+)", files["部署/b.cfg"]).group(1)
    return {"部署/target.txt": "%s:%s\n" % (h, p)}, [[h, p]]

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
