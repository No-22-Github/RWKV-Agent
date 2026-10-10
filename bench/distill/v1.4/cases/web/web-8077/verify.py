# DISTILL-CANARY-844f694e : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'larkfield.gov/parking/permits' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'larkfield-gazette.example.com/parking-permits' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '215' in sec["content"]

print(json.dumps({"expected_string": '215'}, ensure_ascii=False))
