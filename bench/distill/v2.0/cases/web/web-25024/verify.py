# DISTILL-CANARY-3f8c1d24 : distillation case
"""Recompute the build log keep window from the Grimsdale reference page."""
import json
import re

case = json.load(open("case.json"))
page = case["web_fixture"][0]["content"]
logs = int(re.search(r"build_log_keep_days \| (\d+) \|", page).group(1))
binaries = int(re.search(r"binary_keep_days \| (\d+) \|", page).group(1))
if logs == binaries:
    raise SystemExit("the log window and the binary window must differ")
print(json.dumps({"expected_number": logs}))
