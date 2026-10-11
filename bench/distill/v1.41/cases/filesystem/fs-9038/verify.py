# DISTILL-CANARY-068ca07f : distillation case
import json, re
case = json.load(open("case.json"))
assert case["files"]["summary.txt"].startswith("Company summary")
assert case["files"]["reports/q3/chart.csv"].startswith("month,revenue" + chr(10) + "Jul,")
assert case["files"]["reports/q2/summary.txt"].startswith("Quarter: Q2")
text = case["files"]["reports/q3/summary.txt"]
assert text.startswith("Quarter: Q3")
value = int(re.search(r"Revenue: ([0-9]+) USD", text).group(1))
print(json.dumps({"expected_contains_any": [str(value), f"{value:,}"]}))
