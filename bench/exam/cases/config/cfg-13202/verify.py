# EXAM-CANARY-3f1f542b : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
text = case["files"]["deploy/app.yaml"]
new = int(re.search(r"to (\d+)", case["turns"][0]["prompt"]).group(1))
lines = text.split("\n")
sect = None
out = []
for ln in lines:
    if ln and not ln.startswith(" "):
        sect = ln.rstrip(":")
    if sect == "prod" and ln.strip().startswith("workers:"):
        ln = "  workers: %d" % new
    elif sect == "staging" and ln.strip().startswith("workers:"):
        ln = "  workers: %d" % (new // 2)
    out.append(ln)
print(json.dumps({"files": {"deploy/app.yaml": "\n".join(out)}}))
