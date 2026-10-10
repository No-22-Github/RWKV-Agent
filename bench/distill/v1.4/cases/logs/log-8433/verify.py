# DISTILL-CANARY-edfe520b : distillation case
import json

def lineforms(n):
    n = str(n)
    return sorted(["\u7b2c %s \u884c" % n, "\u7b2c%s\u884c" % n, "%s \u884c" % n, "%s\u884c" % n, "line %s" % n, "Line %s" % n, "L%s" % n])

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith('Hospital')
lines = case["files"]['logs/hl7-interface.log'].splitlines()
KEY, MODE = 'NACK from lab system msgid=5F21A9', 'unique'
hits = [i + 1 for i, l in enumerate(lines) if KEY in l]
n = hits[-1] if MODE == "last" else hits[0]
assert (len(hits) == 1) == (MODE == "unique")
print(json.dumps({"expected_contains_any": lineforms(n)}))
