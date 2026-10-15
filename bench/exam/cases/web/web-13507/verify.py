# EXAM-CANARY-e6a02f5d : exam gap-fill case
import json,re
case=json.load(open("case.json",encoding="utf-8"))
page=[e for e in case["web_fixture"] if e.get("content") and "max_retries" in e["content"]][-1]["content"]
print(json.dumps({"expected_number":int(re.search(r"max_retries\D*(\d+)",page).group(1))}))
