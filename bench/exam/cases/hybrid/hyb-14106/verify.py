# EXAM-CANARY-01f004ce : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": {"本周待办.md": case["files"]["本周待办.md"] + "- [ ] 把监控告警阈值发给张莉确认\n- [ ] 预订周五的评审会议室\n"}}))
