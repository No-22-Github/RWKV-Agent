# EXAM-CANARY-a3c3217f : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
conf = case["files"]["conf/services.ini"]
old = "[staging]\nhost = orders.staging.internal\nport = 8443\nrequest_timeout = 30"
assert old in conf
print(json.dumps({"files": {"conf/services.ini": conf.replace(old, old.replace("= 30", "= 60"))}}))
