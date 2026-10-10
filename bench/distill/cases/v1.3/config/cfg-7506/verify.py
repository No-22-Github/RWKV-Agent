# DISTILL-CANARY-37d1a6b8 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
text = files["config/service.yaml"]
facts = []
for line in text.splitlines():
    stripped = line.strip()
    if stripped.startswith("#") and ":" in stripped:
        facts.append(stripped.lstrip("#").split(":")[0].strip())
    elif stripped.startswith("trace_endpoint:"):
        facts.append(stripped.split(":", 1)[1].strip())
    elif stripped.startswith("bulk_export:"):
        facts.append(stripped.split(":")[0].strip())
print(json.dumps({"expected_contains_any": facts}))
