# DISTILL-CANARY-a8d35e41 : distillation case
import json
import re

case = json.load(open("case.json"))
settings = json.loads(case["files"]["config/kiln.json"])

# The trial note states the soak the kiln is fired at for the trial.
note = case["files"]["docs/glaze-trial.md"]
match = re.search(r"soak of (\d+) minutes", note)
if match is None:
    raise SystemExit("the trial note does not state a soak")

target = int(match.group(1))
if settings["soak_minutes"] == target:
    raise SystemExit("fixture already carries the trial soak")

# tools/report_soak.py, which the harness runs against the finished workspace,
# prints this figure back out of the settings file.
print(json.dumps({"expected_stdout": str(target)}))
