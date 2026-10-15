# EXAM-CANARY-77af3190 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
text = case["files"]["conf/gateway.ini"]
head, tail = text.split("\n\n[admin]", 1)
assert "upstream_timeout_sec = 30" in head
# turn 1 sets 60, turn 2 doubles that value and lowers the log level
first = 60
second = first * 2
head = head.replace("upstream_timeout_sec = 30", "upstream_timeout_sec = %d" % second)
head = head.replace("log_level = info", "log_level = warn")
print(json.dumps({"files": {"conf/gateway.ini": head + "\n\n[admin]" + tail}}))
