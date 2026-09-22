# WORKBANK-CANARY-8b31e07a : bank artifact, excluded from training corpora
import json
import re

case = json.load(open("case.json"))
lock = case["files"]["pipeline/deps.lock"]
version = re.search(r"^wrenfield==(\S+)$", lock, re.M).group(1)
pinned = case["files"]["pipeline/requirements.txt"]
updated = re.sub(r"wrenfield==[\d.]+", "wrenfield==" + version, pinned)
print(json.dumps({"files": {"pipeline/requirements.txt": updated}}))
