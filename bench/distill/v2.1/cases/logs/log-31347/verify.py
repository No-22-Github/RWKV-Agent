# DISTILL-CANARY-a3d4597e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd69d597f352e6a1a2a1d93ddf9593cadb6f010706d70f78b503654b506d37ecf', "fixture changed"
import re
ans = str(max(int(x) for x in re.findall(r"resp_ms=(\d+)", case["files"]["logs/access-b.log"])))
assert all(any(s in p or s in t for p, t in case["files"].items()) for s in case["turns"][0]["expect"].get("output_contains", []))
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
assert '1260' in case['turns'][1]['expect']['output_contains']
assert str(ans) == '1260'
