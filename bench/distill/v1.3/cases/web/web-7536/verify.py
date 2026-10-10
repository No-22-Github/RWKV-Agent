# DISTILL-CANARY-37f2761d : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "help.caldermere.example" in e.get("url", ""))
m = re.search(r"minimum stay of (\d+) nights", page["content"])
print(json.dumps({"expected_number": float(m.group(1))}))
