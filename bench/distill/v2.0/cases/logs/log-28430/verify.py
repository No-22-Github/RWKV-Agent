# DISTILL-CANARY-93d8e66b : distillation case
import json

def lineforms(n):
    n = str(n)
    return sorted(["\u7b2c %s \u884c" % n, "\u7b2c%s\u884c" % n, "%s \u884c" % n, "%s\u884c" % n, "line %s" % n, "Line %s" % n, "L%s" % n])

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith('支付网关日志，一天一个文件。')
lines = case["files"]['logs/payment-gw.log'].splitlines()
KEY, MODE = 'switched traffic to standby acquirer acq-b', 'unique'
hits = [i + 1 for i, l in enumerate(lines) if KEY in l]
n = hits[-1] if MODE == "last" else hits[0]
assert (len(hits) == 1) == (MODE == "unique")
print(json.dumps({"expected_contains_any": lineforms(n)}))
