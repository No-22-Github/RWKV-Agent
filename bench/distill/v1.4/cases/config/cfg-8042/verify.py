# DISTILL-CANARY-274a880a : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
token = re.search(r"0x([0-9A-Fa-f]+)", prompt).group(1)
value = int(token, 16)
assert value == 44
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork door access")
assert case["files"]["config/door-access.yaml"].splitlines()[0] == "panel:"
print(json.dumps({"expected_number": value}))
