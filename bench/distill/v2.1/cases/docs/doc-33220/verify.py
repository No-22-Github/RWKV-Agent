# DISTILL-CANARY-97619b69 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0afec65919d6bbe1b0613e656a51f9e648f816fd44f42435d0f0e6601912fc37', "fixture changed"
files = case["files"]
def compute(files):
    out = ""
    for l in files["会议/0911纪要.md"].split("\n"):
        if l.startswith("【待办】"):
            who, rest = l[4:].split("：", 1)
            what, due = rest.rstrip("）").split("（")
            out += "- [ ] %s｜%s｜%s\n" % (what, who, due.replace("前", ""))
    return {"会议/待办清单.md": out}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
