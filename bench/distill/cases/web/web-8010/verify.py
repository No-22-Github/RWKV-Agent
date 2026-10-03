# DISTILL-CANARY-9958b0f2 : distillation case
import json
import re

case = json.load(open("case.json"))
rel = [w for w in case["web_fixture"] if w["url"] == "https://tessera.io/releases"][0]["content"]
print(json.dumps({"expected_string": re.search(r"\| (\d+\.\d+\.\d+) \| stable", rel).group(1)}))
