# DISTILL-CANARY-fc7f27b0 : distillation case
import json, re

case = json.load(open("case.json"))


def load_log(text):
    lines = [l for l in text.splitlines() if l.strip()]
    m = re.search(r"共 (\d+) 行", lines[-1])
    assert m, "缺少完整性页脚"
    assert int(m.group(1)) == len(lines), "行数与页脚不符: %d != %s" % (len(lines), m.group(1))
    return lines



logs = {k: v for k, v in case["files"].items() if k.endswith(".txt")}
assert len(logs) == 2, "应有两轮日志"
for k in sorted(logs):
    load_log(logs[k])
target = [k for k in logs if "0929" in k]
assert len(target) == 1, "应恰好选中一份日志: %s" % target
lines = load_log(logs[target[0]])
assert "2026-09-29" in lines[0], "选中的日志头不是 9 月 29 日"

fails = [l for l in lines if l.startswith("FAIL ")]
print(json.dumps({"expected_number": len(fails)}))
