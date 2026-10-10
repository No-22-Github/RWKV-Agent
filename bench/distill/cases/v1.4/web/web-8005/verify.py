# DISTILL-CANARY-17f45024 : distillation case
import json
import re

case = json.load(open("case.json"))
rel = [w for w in case["web_fixture"] if w["url"] == "https://meridiandb.org/releases"][0]["content"]
ver = re.search(r"\| (\d+\.\d+\.\d+) \| \d{4}-\d\d-\d\d \| GA", rel).group(1)
print(json.dumps({"expected_string": ver}))
