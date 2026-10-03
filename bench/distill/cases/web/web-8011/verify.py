# DISTILL-CANARY-928bd6a3 : distillation case
import json
import re

case = json.load(open("case.json"))
rel = [w for w in case["web_fixture"] if "github.com/kestrel-labs" in w["url"]][0]["content"]
print(json.dumps({"expected_string": re.search(r"## v(\d+\.\d+\.\d+) \(latest\)", rel).group(1)}))
