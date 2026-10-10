# DISTILL-CANARY-777635dc : distillation case
import json

def lineforms(n):
    n = str(n)
    return sorted(["\u7b2c %s \u884c" % n, "\u7b2c%s\u884c" % n, "%s \u884c" % n, "%s\u884c" % n, "line %s" % n, "Line %s" % n, "L%s" % n])

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith('小费分摊规则。')
lines = case["files"]['src/TipRules.java'].splitlines()
d = [i + 1 for i, l in enumerate(lines) if l.startswith('    static int roundTipAmount(')]
assert len(d) == 1
print(json.dumps({"expected_contains_any": lineforms(d[0])}))
