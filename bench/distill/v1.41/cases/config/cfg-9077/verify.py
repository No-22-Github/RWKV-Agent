# DISTILL-CANARY-83e86f82 : distillation case
import json
case = json.load(open("case.json"))
text = case["files"]["config/server.toml"]
assert text.startswith("[http]") and "read_timeout_s = 45" in text
assert "read_timeout_s = 30" in case["files"]["config/server.toml.bak"]
print(json.dumps({"expected_number": 45}))
