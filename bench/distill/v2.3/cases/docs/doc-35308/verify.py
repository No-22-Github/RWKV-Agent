# DISTILL-CANARY-f5aeb502 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '13d8c6106c223a3b137bbf99612156750df39a34517f7fd299b7a05204657a3b', "fixture changed"
OPS = json.loads('[["sub", "纪要/产品周会-0911.md", "## 待定\\n- 是否上线深色模式\\n- 海外站点的支付渠道\\n- 会员体系是否并入\\n\\n## 行动项\\n- 张岚：整理灰度名单\\n", "## 行动项\\n- 张岚：整理灰度名单\\n- 周屿：跟进深色模式排期\\n- 陈默：确认海外支付渠道清单\\n"]]')
end = dict(files)
for op in OPS:
    kind, path = op[0], op[1]
    if kind == "sub":
        assert end[path].count(op[2]) == 1, (path, op[2])
        end[path] = end[path].replace(op[2], op[3])
    elif kind == "set":
        end[path] = op[2]
    else:
        t = end[path]
        end[path] = (t if t.endswith("\n") or not t else t + "\n") + op[2]
print(json.dumps({"files": {p: t for p, t in end.items() if files.get(p) != t}}, ensure_ascii=False))
