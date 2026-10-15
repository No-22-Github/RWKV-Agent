# EXAM-CANARY-b7d3e1c8 : exam gap-fill case
import json
case=json.load(open("case.json",encoding="utf-8"))
def m(x): h,mm=x.split(":"); return int(h)*60+int(mm)
w=[]
for l in case["files"]["data/tickets.tsv"].splitlines()[1:]:
    t,p,o,c=l.split("\t")
    if c and p!="test": w.append(m(c)-m(o))
print(json.dumps({"expected_number":round(sum(w)/len(w),1)}))
