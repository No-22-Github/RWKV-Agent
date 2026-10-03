# DISTILL-CANARY-75b1ba2a : distillation case
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("边缘代理配置")
assert "proxy_read_timeout" in case["files"]["nginx/conf.d/upstream.conf"]
print(json.dumps({"expected_contains_any": ["超时"]}, ensure_ascii=False))
