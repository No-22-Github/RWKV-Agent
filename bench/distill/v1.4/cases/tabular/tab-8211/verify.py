# DISTILL-CANARY-c5d35103 : distillation case
import csv
import hashlib
import io
import json

case = json.load(open("case.json"))
spec = json.loads('{"cols": {"date": "日期", "flt": null, "grp": "花束", "id": "订单号", "qty": "数量", "val": "单价"}, "fmt": "csv", "ftgt": null, "nowrite": ["无法写", "没法写", "不能写", "没有写文件", "没有写入", "没有写工具", "写不了", "无法保存", "没法保存", "不能保存", "手动", "自己保存", "自己写", "需要你自己", "无法创建", "没法创建", "不能创建", "只读", "没法追加", "无法追加", "不能追加", "无法写入", "没法写入", "不能写入", "没办法写", "没办法保存", "没办法追加", "没有写权限", "没有写入权限", "自行写入", "自行保存", "自行追加", "没能写", "没法把", "无法把", "没写成", "未能写入", "写入权限", "写文件权限", "写入能力", "写文件的能力", "写入工具", "写文件的工具", "写入功能", "可写"], "op": "expr", "path": "订单/花束订单.csv", "prec": 2, "sha": {"README.md": "bba312c6a1b8036a0b49d4b119e75795cb5eff978ff99d32a2b4df2c4102d331", "订单/花束订单.csv": "21988ffe4e262b393e5e75f83065f68425ac0bf3a9e5f93fbac17c1e90f3c292", "账本/.keep": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}, "tgt": "红玫瑰"}')
if not spec.get("nocheck"):
    for _p, _h in spec["sha"].items():
        assert hashlib.sha256(case["files"][_p].encode()).hexdigest() == _h, _p
    assert sorted(case["files"]) == sorted(spec["sha"])
text = case["files"][spec["path"]]
if spec["fmt"] == "csv":
    rows = list(csv.DictReader(io.StringIO(text)))
else:
    rows = [json.loads(l) for l in text.splitlines() if l.strip()]
c = spec["cols"]
sel = [r for r in rows if c.get("flt") is None or str(r[c["flt"]]) == spec["ftgt"]]
tg = [r for r in sel if str(r[c["grp"]]) == spec["tgt"]]
op = spec["op"]
name = None
if op == "sum":
    x = sum(float(r[c["val"]]) for r in tg)
elif op == "count":
    x = len(tg)
elif op == "max":
    x = max(float(r[c["val"]]) for r in tg)
elif op == "expr":
    x = sum(float(r[c["qty"]]) * float(r[c["val"]]) for r in tg)
elif op == "share":
    x = 100.0 * sum(float(r[c["val"]]) for r in tg) / sum(float(r[c["val"]]) for r in sel)
else:
    tot = {}
    for r in sel:
        tot[r[c["grp"]]] = tot.get(r[c["grp"]], 0) + float(r[c["val"]])
    ranked = sorted(tot.items(), key=lambda kv: kv[1], reverse=(op == "top"))
    assert round(ranked[0][1], 6) != round(ranked[1][1], 6)
    name, x = ranked[0]
x = int(x) if op == "count" else round(x, spec["prec"])
print(json.dumps({"expected_number": x, "expected_name": name, "expected_contains_any": spec["nowrite"]}, ensure_ascii=False))
