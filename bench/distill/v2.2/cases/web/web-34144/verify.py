# DISTILL-CANARY-2fcb4d2f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3de3e9e9d9758c5d756bbcf7c31dcaaa335c6253b47c1f8a99f51b0ae0816588', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in prompts or item in [], item
for url in [w["url"] for w in case["web_fixture"]]:
    assert url, url
def compute(files, web):
    t = files["notes/budget.md"].replace("健身年卡 1500 元（待确认）", "健身年卡 1680 元")
    return {"notes/budget.md": t}, []

FINAL, _ = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: FINAL[k] for k in case["expect"]["files"] if k in FINAL}}, ensure_ascii=False))
