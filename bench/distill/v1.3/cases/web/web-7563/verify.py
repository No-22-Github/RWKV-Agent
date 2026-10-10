# DISTILL-CANARY-756de73c : distillation case
import json
import re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.cragwellradio.example/cr40/firmware" in e.get("url", ""))
match = re.search(r"cr40-fw-(\d+\.\d+\.\d+)\.pkg - current stable", page["content"])
print(json.dumps({"expected_string": match.group(1)}))
