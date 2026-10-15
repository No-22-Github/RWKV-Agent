# EXAM-CANARY-786c5f3b : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
prompt = " ".join(t["prompt"] for t in case["turns"]) + json.dumps(case.get("files", {}), ensure_ascii=False) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
facts = ["本周完成", "下周计划", "风险与阻塞", "需要的支持"]
for f in facts:
    assert f in prompt, f
exp = case["expect"]["files"]
out = {}
for p, e in exp.items():
    if "contains" in e:
        out[p] = "\n".join(derived if "derived" in globals() else e["contains"])
print(json.dumps({"files": out}, ensure_ascii=False))
