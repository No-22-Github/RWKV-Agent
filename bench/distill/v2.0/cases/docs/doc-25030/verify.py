# DISTILL-CANARY-6b2e93c8 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
listed = [line.strip() for line in files["registers/protocol-set.txt"].splitlines() if line.strip()]

# A register entry resolves only when a protocol sits at exactly that path; the
# file whose name carries the extra word is not the file the register names.
missing = [path for path in listed if path not in files]
print(json.dumps({"expected_string": missing[0] if missing else "UNKNOWN"}))
