# EXAM-CANARY-df5139d5 : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
text = case["files"]["notes/standup-0914.md"]
sec = text.split("##")[0]
out = ""
for ln in sec.splitlines():
    m = re.match(r"- (\w+) to (.+) by (\d+ \w+)( \(done\))?$", ln)
    if m and not m.group(4):
        out += "- %s: %s (%s)\n" % (m.group(1), m.group(2), m.group(3))
print(json.dumps({"files": {"todo.md": out}}))
