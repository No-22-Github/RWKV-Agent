# EXAM-CANARY-92d5b7e4 : exam gap-fill case
import json,re
case=json.load(open("case.json",encoding="utf-8"))
page=[e for e in case["web_fixture"] if e.get("content") and "Uploads" in e["content"]][-1]["content"]
print(json.dumps({"expected_number":int(re.search(r"Uploads\D*(\d+)",page).group(1))}))
