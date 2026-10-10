# DISTILL-CANARY-3567732d : distillation case
import json

case = json.load(open("case.json"))
f = case["files"]
assert f["tutoring/README.md"].startswith("BrightPath Tutoring Center")
counts = {}
for subj in ("math", "reading", "writing"):
    counts[subj] = len([p for p in f if p.startswith("tutoring/handouts/%s/" % subj) and p.endswith(".md")])
assert counts == {"math": 3, "reading": 2, "writing": 2}, counts
prompt = case["turns"][1]["prompt"].lower()
chosen = [s for s in ("math", "reading", "writing") if s in prompt]
assert len(chosen) == 2, chosen
ask = ["which subjects", "Which subjects", "which two", "which folders", "name the subjects", "subjects you want", "Which two"]
print(json.dumps({"expected_number": counts[chosen[0]], "expected_contains_any": ask}, ensure_ascii=False))
