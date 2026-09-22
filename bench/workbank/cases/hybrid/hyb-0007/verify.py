# WORKBANK-CANARY-c9d40f16 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if e.get("url", "").endswith("/releases"))
entries = re.findall(r"^## (\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\)", page["content"], re.M)
version = max(entries, key=lambda item: item[1])[0]
pinned = case["files"]["tools/requirements.txt"]
updated = re.sub(r"saltmarsh==[\d.]+", "saltmarsh==" + version, pinned)
print(json.dumps({"files": {"tools/requirements.txt": updated}}))
