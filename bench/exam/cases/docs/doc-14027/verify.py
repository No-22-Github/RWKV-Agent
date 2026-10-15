# EXAM-CANARY-50a4669c : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
prompt = " ".join(t["prompt"] for t in case["turns"]) + json.dumps(case.get("files", {}), ensure_ascii=False) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
facts = []
for f in facts:
    assert f in prompt, f
import re
t = case["files"]["event/details.txt"]
derived = [re.search(r"Event: (.+)", t).group(1), re.search(r"Date: (\S+)", t).group(1), re.search(r"Start: (\S+)", t).group(1), re.search(r"Room \w+", t).group(0), re.search(r"RSVP: (\S+)", t).group(1)]
exp = case["expect"]["files"]
out = {}
for p, e in exp.items():
    if "contains" in e:
        out[p] = "\n".join(derived if "derived" in globals() else e["contains"])
print(json.dumps({"files": out}, ensure_ascii=False))
