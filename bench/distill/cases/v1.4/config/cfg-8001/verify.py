# DISTILL-CANARY-10210878 : distillation case
def kv(text):
    out = {}
    for line in text.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out

import json

case = json.load(open("case.json"))
files = case["files"]
required = [l.strip()[2:] for l in files["平台/必填键.yaml"].splitlines() if l.strip().startswith("- ")]
assert files["平台/必填键.yaml"].splitlines()[0] == "必填键:"
stations = {p.split("/")[1][:-5]: kv(t) for p, t in files.items() if p.startswith("站点/")}
# No passenger pier called 南湾码头 is configured: every 客运码头 file has all required keys, and the
# only 南湾 file is a freight yard that does not sell tickets.
assert "南湾码头" not in stations
nanwan = [n for n in stations if n.startswith("南湾")]
assert nanwan == ["南湾货运堆场"] and stations["南湾货运堆场"]["站点类型"] == "货运堆场"
for name, s in stations.items():
    if s.get("站点类型") == "客运码头":
        assert all(k in s for k in required), name
plan = files["运营/上线排期.md"]
assert any("南湾码头" in l and "待提交" in l for l in plan.splitlines())
neg = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "待提交", "未提交", "没提交"]
print(json.dumps({"expected_contains_any": neg}, ensure_ascii=False))
