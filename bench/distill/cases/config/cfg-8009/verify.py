# DISTILL-CANARY-fa63d11e : distillation case
import json
import re

case = json.load(open("case.json"))
lock = case["files"]["poetry.lock"]
ver = re.search(r'name = "httpx"\nversion = "([^"]+)"', lock).group(1)
req = case["files"]["requirements.txt"]
assert req.startswith("fastapi==")
print(json.dumps({"files": {"requirements.txt": re.sub(r"^httpx==.*$", "httpx==" + ver, req, flags=re.M)}}))
