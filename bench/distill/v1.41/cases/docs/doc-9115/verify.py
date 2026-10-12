# DISTILL-CANARY-d30fc2e8 : distillation case
import json
case = json.load(open("case.json"))
text = case["files"]["docs/RELEASE.md"]
assert text.startswith("# 发布状态") and "当前稳定版：3.1.2" in text
assert case["files"]["docs/INSTALL.md"].startswith("# 安装") and "3.0.4" in case["files"]["docs/INSTALL.md"]
print(json.dumps({"expected_contains_any": ["3.1.2"]}))
