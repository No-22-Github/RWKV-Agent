# DISTILL-CANARY-72f0b6d9 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import re
text = files["config/backup.yaml"]
def value(key):
    for line in text.splitlines():
        if line.startswith(key + ":"):
            return line.split(":", 1)[1].strip()
facts = [value("target"),
         re.sub("\"", "", value("schedule")).split()[0],
         value("retention_days")]
print(json.dumps({"expected_contains_any": facts}))
