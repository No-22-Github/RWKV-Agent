# EXAM-CANARY-b3aea087 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
sec = case["files"]["conf/server.ini"].split("[staging]")[0]
vals = dict(l.split(" = ") for l in sec.splitlines() if " = " in l)
print(json.dumps({"expected_contains_all": [vals["port"], vals["host"], vals["workers"]]}))
