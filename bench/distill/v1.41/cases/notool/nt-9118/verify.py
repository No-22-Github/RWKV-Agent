# DISTILL-CANARY-73a5d045 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {"配置/web.conf": "listen 8080\n", "配置/api.conf": "listen 8080\n", "配置/admin.conf": "listen 8080\n"}
print(json.dumps({"expected_contains_any": ["sed -i"]}, ensure_ascii=False))
