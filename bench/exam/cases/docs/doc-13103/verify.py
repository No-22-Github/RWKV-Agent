# EXAM-CANARY-582e72b2 : exam gap-fill case
import json, re

case = json.load(open("case.json", encoding="utf-8"))
note = case["files"]["会议/0916站会.md"]
todo = note.split("## 待办")[1].split("##")[0]
items = []
for line in todo.splitlines():
    m = re.match(r"- (\S+)：(.+?)，(?:截止 (\d+)月(\d+)日|时间还没定)。", line)
    if not m:
        continue
    who, what, mo, d = m.groups()
    if who == "小周":  # turn 2: handed over, removed
        continue
    key = (int(mo), int(d)) if mo else (99, 99)
    date = "%s月%s日" % (mo, d) if mo else "待定"
    items.append((key, "- [ ] %s：%s（%s）" % (who, what, date)))
items.sort()
print(json.dumps({"files": {"todo.md": "\n".join(t for _, t in items) + "\n"}}, ensure_ascii=False))
