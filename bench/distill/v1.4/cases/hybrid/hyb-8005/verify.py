# DISTILL-CANARY-26b77675 : distillation case
import json
import re

case = json.load(open("case.json"))
base = float(re.search(r"(\d+) 元/批", case["files"]["采购/均价.md"]).group(1))
cpi = float(re.search(r"同比上涨 ([\d.]+)%", case["web_fixture"][0]["content"]).group(1))
v = round(base * (1 + cpi / 100), 2)
s = lambda x: x.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({s("%.2f" % v), s("{:,.2f}".format(v))})}))
