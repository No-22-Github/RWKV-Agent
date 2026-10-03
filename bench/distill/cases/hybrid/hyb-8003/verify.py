# DISTILL-CANARY-ba892226 : distillation case
import json
import re

case = json.load(open("case.json"))
page = [w for w in case["web_fixture"] if w["url"] == "https://tidewater.dev/releases"][0]["content"]
stable = [m.group(1) for m in re.finditer(r"\| (5\.3\.\d+) \| stable \|", page)]
best = max(stable, key=lambda v: int(v.split(".")[2]))
assert case["files"]["README.md"].startswith("Gateway service image. Stay on the 5.3 series")
src = case["files"]["Dockerfile"]
assert src.startswith("FROM ghcr.io/tidewater/runtime:5.3.")
new = re.sub(r"runtime:5\.3\.\d+", "runtime:" + best, src, count=1)
print(json.dumps({"files": {"Dockerfile": new}}))
