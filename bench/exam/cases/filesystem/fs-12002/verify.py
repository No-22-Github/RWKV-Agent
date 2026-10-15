# EXAM-CANARY-7b95f028 : sol pilot case
import json
case=json.load(open("case.json",encoding="utf-8"))
rule=json.loads(case["files"]["缓存/清理口径.json"])
retained={}
for path,text in case["files"].items():
    relative=path[len(rule["root"]):] if path.startswith(rule["root"]) else None
    remove=relative is not None and path.endswith(rule["suffix"]) and relative not in rule["preserve"]
    if not remove:
        retained[path]=text
print(json.dumps({"files":retained},ensure_ascii=False))
