# DISTILL-CANARY-a5294043 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["config/compressors.yaml"]
block = [
    "compressor_3:",
    "  refrigerant: R404A",
    "  cutout_c: -18",
    "  service_due_h: 0",
]
derived = text.rstrip("\n") + "\n" + "\n".join(block) + "\n"
print(json.dumps({"files": {"config/compressors.yaml": derived}}))
