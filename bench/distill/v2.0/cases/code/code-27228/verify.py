# DISTILL-CANARY-a3ccd14e : distillation case
import json, re

case = json.load(open("case.json"))


def load_log(text):
    lines = [l for l in text.splitlines() if l.strip()]
    m = re.search(r"共 (\d+) 行", lines[-1])
    assert m, "缺少完整性页脚"
    assert int(m.group(1)) == len(lines), "行数与页脚不符: %d != %s" % (len(lines), m.group(1))
    return lines



logs = {k: v for k, v in case["files"].items() if k.endswith(".txt")}
assert len(logs) == 1, "应恰好有一份日志"
lines = load_log(list(logs.values())[0])

fails = [l for l in lines if l.startswith("FAIL ")]
print(json.dumps({"expected_number": len(fails)}))
