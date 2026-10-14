# DISTILL-CANARY-47f330ad : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a8fa20b0aade5faf2117ec2d209cace92267bf27cc50143ea035e014030609f1', "fixture changed"
m = re.search('(0755-5550-188)', case["files"]['食堂/订餐.md'])
assert m and m.group(1) == '0755-5550-188'
print(json.dumps({"expected_string": '0755-5550-188'}, ensure_ascii=False))
