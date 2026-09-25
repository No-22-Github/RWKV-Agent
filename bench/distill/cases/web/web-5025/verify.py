# DISTILL-CANARY-7a2e5b90 : distillation case
"""Recompute the build a plain Pellumbra install picks up from the releases page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
rows = re.findall(r"\| ([\d.]+(?:-rc\d+)?) \| (\w+) \| (\d+) \|", page)
stable = [int(build) for _release, channel, build in rows if channel == "stable"]
candidates = [int(build) for _release, channel, build in rows if channel == "candidate"]
if len(stable) < 2 or not candidates:
    raise SystemExit("the release table must carry two stable builds and one candidate")
answer = max(stable)
if answer in candidates:
    raise SystemExit("the newest stable build must not be a candidate")
print(json.dumps({"expected_number": answer}))
