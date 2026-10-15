# EXAM-CANARY-0f6c83d2 : exam gap-fill case
import json,collections
case=json.load(open("case.json",encoding="utf-8"))
c=collections.Counter()
for l in case["files"]["logs/access.log"].splitlines():
    ts,m,p,st,d=l.split()
    if int(st)<500: c[ts[11:13]]+=1
print(json.dumps({"expected_number":max(c.values())}))
