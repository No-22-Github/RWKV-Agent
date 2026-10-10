# DISTILL-CANARY-71b3d86e : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]

# Every path named by the register is checked against the folder; a drawing
# named twice is still one drawing.
named = [line.strip() for line in files["register/parts-register.txt"].splitlines() if line.strip()]
missing = {path for path in named if path not in files}

print(json.dumps({"expected_number": len(missing)}))
