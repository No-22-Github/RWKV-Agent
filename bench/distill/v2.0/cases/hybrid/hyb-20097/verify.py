# DISTILL-CANARY-bad7d547 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '3708b76823a4aa141511bff24ccfd8508b583dcd26ae471a9b283b2b528eb5a6', "fixture changed"
m = re.search('2026-09-14 Osaka Showers 22-(27)C', case["files"]['logs/weather-log.txt'])
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
