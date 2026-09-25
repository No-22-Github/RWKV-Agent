# DISTILL-CANARY-b64a0d58 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
listed = [line.strip() for line in files["checklists/site-pack.txt"].splitlines() if line.strip()]

# A listed path resolves only when a file sits at exactly that path; the
# similarly named file in guides/ is not the one the list names.
missing = [path for path in listed if path not in files]
print(json.dumps({"expected_string": missing[0] if missing else "UNKNOWN"}))
