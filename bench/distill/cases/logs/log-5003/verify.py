# DISTILL-CANARY-8bbbd3ee : distillation case
import json
import re

case = json.load(open("case.json"))
lines = [line for line in case["files"]["logs/relay.log"].splitlines() if line.strip()]
first_error = [line for line in lines if " ERROR " in line][0]
pending = re.search(r"pending=(\d+)$", first_error).group(1)
print(json.dumps({"expected_number": int(pending)}))
