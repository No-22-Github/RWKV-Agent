# DISTILL-CANARY-928523d0 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if "docs.sablewood.io" in w["url"]][0]
wiki = [w for w in case["web_fixture"] if "devcommons" in w["url"]][0]["content"]
assert off.get("error")
print(json.dumps({"expected_number": int(re.search(r"capped at (\d+) MB", wiki).group(1))}))
