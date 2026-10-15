# EXAM-CANARY-4f20170b : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
def port(env):
    m = re.search(r"^port:\s*(\d+)", files["config/payments.%s.yaml" % env], re.M)
    return m.group(1) if m else re.search(r"^port:\s*(\d+)", files["config/payments.base.yaml"], re.M).group(1)
assert port("staging") != re.search(r"^port:\s*(\d+)", files["config/payments.base.yaml"], re.M).group(1)
assert port("prod") == case["turns"][0]["expect"]["output_contains"][0]
print(json.dumps({"expected": port("staging")}))
