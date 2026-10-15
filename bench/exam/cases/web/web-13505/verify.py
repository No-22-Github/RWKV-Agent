# EXAM-CANARY-1c8f3a96 : exam gap-fill case
import json,re
case=json.load(open("case.json",encoding="utf-8"))
page=[e for e in case["web_fixture"] if e.get("content") and "request_timeout" in e["content"]][-1]["content"]
print(json.dumps({"expected_number":int(re.search(r"request_timeout\D*(\d+)",page).group(1))}))
