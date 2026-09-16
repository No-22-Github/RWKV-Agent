import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"]
match = re.search(r"Registered office[^:\n]*:\s*(.+)", readme)
address = match.group(1).strip() if match else None
print(json.dumps({"expected": address}))
