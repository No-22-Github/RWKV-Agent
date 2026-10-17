# DISTILL-CANARY-aac1f17d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c7a535e7d0b9f8927f7695247bfe903cd61cf6c3911c318935e1fc58ea57445b', "fixture changed"
def compute(files, web):
    import re
    pg = [w for w in web if "chicheng" in w["url"]][0]["content"]
    pr = dict((k, int(v)) for k, v in re.findall(r"(\S+)：(\d+) 元/天", pg))

    def tot(t):
        car = re.search(r"车型：(\S+)", t).group(1)
        return pr[car] * int(re.search(r"用车天数：(\d+)", t).group(1))
    return {}, [[str(tot(files["出差/行程.txt"]))], [str(tot(files["出差/备选方案.txt"]))]]

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
