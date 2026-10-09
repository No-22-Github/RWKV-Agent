# DISTILL-CANARY-cd51adbb : distillation case
import json, re
case = json.load(open("case.json"))
assert case["files"]["合同/README.md"] == "模板最后修订：2026-07。" + chr(10)
text = case["files"]["合同/采购框架协议模板.md"]
assert text.startswith("# 采购框架协议（模板）")
m = re.search(r"每逾期一日按未交付部分货款的 ([0-9.]+%) 支付违约金", text)
print(json.dumps({"expected_string": m.group(1)}))
