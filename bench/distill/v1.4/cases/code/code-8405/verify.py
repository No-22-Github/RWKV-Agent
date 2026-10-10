# DISTILL-CANARY-49768931 : distillation case
import json

def lineforms(n):
    n = str(n)
    return sorted(["\u7b2c %s \u884c" % n, "\u7b2c%s\u884c" % n, "%s \u884c" % n, "%s\u884c" % n, "line %s" % n, "Line %s" % n, "L%s" % n])

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith('快递面单解析。')
lines = case["files"]['express/waybill.py'].splitlines()
d = [i + 1 for i, l in enumerate(lines) if l.startswith('def parse_waybill_code(')]
assert len(d) == 1
print(json.dumps({"expected_contains_any": lineforms(d[0])}))
