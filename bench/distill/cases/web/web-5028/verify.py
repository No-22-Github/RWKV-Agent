# DISTILL-CANARY-8b0f4c52 : distillation case
"""Recompute the busy sweep interval from the Bracklowe defaults page."""
import json
import re

case = json.load(open("case.json"))
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
busy = int(re.search(r"busy_sweep_interval_minutes \| (\d+) \|", pages).group(1))
idle = int(re.search(r"idle_sweep_interval_minutes \| (\d+) \|", pages).group(1))
trial = int(re.search(r"trial workspace is swept every (\d+) minutes", pages).group(1))
if len({busy, idle, trial}) != 3:
    raise SystemExit("the busy, idle and trial intervals must differ")
print(json.dumps({"expected_number": busy}))
