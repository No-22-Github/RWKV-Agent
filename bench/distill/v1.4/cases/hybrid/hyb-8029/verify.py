# DISTILL-CANARY-9d2f1be9 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://mallowdb.example/support/lifecycle'][0]["content"]
files = case["files"]
f = files["ops/runbook.yaml"]
series = re.match(r"version: (\d+\.\d+)\.", f).group(1)
val = re.search(r"\| %s \| (\d{4}-\d\d-\d\d) \|" % re.escape(series), off).group(1)
assert val == '2027-05-14'
print(json.dumps({"expected_contains_any": ["2027-05-14", "14 May 2027", "May 14, 2027", "May 2027", "14 May, 2027"]}, ensure_ascii=False))
