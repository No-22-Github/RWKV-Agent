# DISTILL-CANARY-8dc17655 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0a5524c1e6f0ba2d2bd8ac9b59ffcbbc46c83b08ace68fe0a229ec55849bb7d3', "fixture changed"
m = re.search('2026-09-10 东京 晴 25~(31)℃', case["files"]['旅行/天气备忘.txt'])
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
