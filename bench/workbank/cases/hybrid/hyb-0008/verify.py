# WORKBANK-CANARY-2e7b6a53 : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if e.get("url", "").endswith("/releases"))
entries = re.findall(r"^## (\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\)", page["content"], re.M)
version = max(entries, key=lambda item: item[1])[0]
dev = case["files"]["requirements/dev.txt"]
updated = re.sub(r"piperock==[\d.]+", "piperock==" + version, dev)
print(json.dumps({"files": {"requirements/dev.txt": updated}}))
