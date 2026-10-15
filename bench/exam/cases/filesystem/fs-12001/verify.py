# EXAM-CANARY-3a64ed91 : sol pilot case
import json
from pathlib import PurePosixPath
case=json.load(open("case.json",encoding="utf-8"))
prompt=case["turns"][0]["prompt"]
import re
root,old,new=re.findall(r"`([^`]+)`",prompt)
result={}
for path,text in case["files"].items():
    if path.startswith(root) and PurePosixPath(path).suffix==".md":
        result[path]=text.replace(old,new)
    else:
        result[path]=text
print(json.dumps({"files":result},ensure_ascii=False))
