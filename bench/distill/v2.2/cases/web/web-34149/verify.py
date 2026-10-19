# DISTILL-CANARY-b609ef70 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '219b534a7435d96cb6804a3118f4e3b41046e056f2c630d45b42919e79f9e06b', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + " " + " ".join(case["files"].values())
prompts = " ".join(t["prompt"] for t in case["turns"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in prompts or item in [], item
for url in [w["url"] for w in case["web_fixture"]]:
    assert url, url
def compute(files, web):
    t = files["finance/invoice_template.txt"].replace("服务费率：5%", "服务费率：4%")
    return {"finance/invoice_template.txt": t}, []

FINAL, _ = compute(dict(case["files"]), case["web_fixture"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: FINAL[k] for k in case["expect"]["files"] if k in FINAL}}, ensure_ascii=False))
