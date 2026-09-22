# WORKBANK-CANARY-4f2a91cd : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if e.get("url", "").endswith("/changelog"))
entries = re.findall(r"^## (\d+\.\d+\.\d+) \((\d{4}-\d{2}-\d{2})\)", page["content"], re.M)
version = max(entries, key=lambda item: item[1])[0]
pinned = case["files"]["service/requirements.txt"]
updated = re.sub(r"kestrelplot==[\d.]+", "kestrelplot==" + version, pinned)
print(json.dumps({"files": {"service/requirements.txt": updated}}))
