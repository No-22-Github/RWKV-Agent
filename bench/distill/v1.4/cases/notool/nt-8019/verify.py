# DISTILL-CANARY-46e94cf8 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
packs = int(re.search(r"(\d+) packs", prompt).group(1))
per = int(re.search(r"(\d+) bags in each pack", prompt).group(1))
print(json.dumps({"expected_number": packs * per}))
