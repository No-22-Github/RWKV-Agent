# DISTILL-CANARY-4f499b01 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["配置/说明.md"].startswith("循环泵参数")
flows = {}
for pump in ("1号泵", "2号泵", "3号泵"):
    m = re.search(r"流量立方米每小时:\s*(\d+)", f["配置/循环泵/%s.yaml" % pump])
    assert m, pump
    flows[pump] = int(m.group(1))
ask = ["哪两台", "哪几台", "哪两台泵", "哪几台泵", "位号", "设备编号", "泵编号", "泵的编号"]
print(json.dumps({"expected_number": flows["2号泵"], "expected_contains_any": ask}, ensure_ascii=False))
