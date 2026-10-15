# EXAM-CANARY-6f9c283b : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
print(json.dumps({"files": {"conf/net.ini": case["files"]["conf/net.ini"].replace("[prod]\nhost = api.prod.internal\nport = 8080", "[prod]\nhost = api.prod.internal\nport = 9443").replace("port = 8081\nretries = 3", "port = 9443\nretries = 5")}}))
