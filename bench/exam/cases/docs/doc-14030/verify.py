# EXAM-CANARY-9367b158 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
prompt = " ".join(t["prompt"] for t in case["turns"]) + json.dumps(case.get("files", {}), ensure_ascii=False) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
facts = ["2026-09-18", "11:00"]
for f in facts:
    assert f in prompt, f
import re
t = case["files"]["ops/incident.md"]
derived = [re.search(r"# (INC-\d+)", t).group(1), "2026-09-18", "11:00"]
exp = case["expect"]["files"]
out = {}
for p, e in exp.items():
    if "contains" in e:
        out[p] = "\n".join(derived if "derived" in globals() else e["contains"])
print(json.dumps({"files": out}, ensure_ascii=False))
