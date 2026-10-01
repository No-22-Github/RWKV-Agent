# DISTILL-CANARY-a4d4dc67 : distillation case
import json, re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "geo.yantai.example/docs/quota" in e.get("url", ""))
m = re.search(r"逆地理编码\s*\|\s*批量接口并发上限为\s*(\d+)", page["content"])
assert m, "配额行缺失"
print(json.dumps({"expected_number": int(m.group(1))}))
