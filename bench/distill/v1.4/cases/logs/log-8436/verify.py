# DISTILL-CANARY-04c3dbb0 : distillation case
import json

def lineforms(n):
    n = str(n)
    return sorted(["\u7b2c %s \u884c" % n, "\u7b2c%s\u884c" % n, "%s \u884c" % n, "%s\u884c" % n, "line %s" % n, "Line %s" % n, "L%s" % n])

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith('智能电表集中器网关日志。')
lines = case["files"]['logs/meter-gateway.log'].splitlines()
KEY, MODE = 'meter 00A7F2 over-voltage alarm cleared', 'unique'
hits = [i + 1 for i, l in enumerate(lines) if KEY in l]
n = hits[-1] if MODE == "last" else hits[0]
assert (len(hits) == 1) == (MODE == "unique")
print(json.dumps({"expected_contains_any": lineforms(n)}))
