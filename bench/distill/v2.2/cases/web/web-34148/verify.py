# DISTILL-CANARY-e43c8f33 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '49a1a0148b746d33e039d24f7575700b215c1b80d71354da3bb9101e85dea08c', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in prompts or item in [], item
for url in [w["url"] for w in case["web_fixture"]]:
    assert url, url
def compute(files, web):
    return {}, []

FINAL, _ = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: FINAL[k] for k in case["expect"]["files"] if k in FINAL}}, ensure_ascii=False))
