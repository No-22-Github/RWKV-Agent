# DISTILL-CANARY-30fba594 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '04fbcf25e099233a77ad9586f5d22ced6af1580e8343fb53a10e38fd3e48a1fb', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in prompts or item in [], item
for url in [w["url"] for w in case["web_fixture"]]:
    assert url, url
def compute(files, web):
    t = files["requirements.txt"].replace("tablekit==2.7.1", "tablekit==2.8.4")
    return {"requirements.txt": t}, []

FINAL, _ = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: FINAL[k] for k in case["expect"]["files"] if k in FINAL}}, ensure_ascii=False))
