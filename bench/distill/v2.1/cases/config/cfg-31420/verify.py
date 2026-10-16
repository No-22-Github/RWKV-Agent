# DISTILL-CANARY-eddf11eb : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '30a0c43da3d77b8b0c063aca2fe2128413af43e3740e7f327a77a5b47e8ec9ed', "fixture changed"
import re
m = re.search('\\| billing \\| (\\d+) \\|', case["files"]['service/ports.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]
assert 'Elasticsearch' not in ans

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
