# DISTILL-CANARY-bf47138d : distillation case
"""Recompute the SM-4402 wait from the Stanmere rate window page."""
import json
import re

case = json.load(open("case.json"))
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
wait = int(re.search(r"the caller is asked to wait (\d+) seconds", pages).group(1))
lock = int(re.search(r"released after (\d+) seconds", pages).group(1))
if wait == lock:
    raise SystemExit("the rate window wait and the key lock must differ")
print(json.dumps({"expected_number": wait}))
