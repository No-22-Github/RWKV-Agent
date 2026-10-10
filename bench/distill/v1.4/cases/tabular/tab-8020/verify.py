# DISTILL-CANARY-700bbce1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files['检测/2026-09.csv'].splitlines()[0] == '单号,日期,桥梁,费用'
assert files['桥梁/编码表.csv'].splitlines()[0] == '编码,桥梁,状态,说明'
ledger = list(csv.DictReader(io.StringIO(files['检测/2026-09.csv'])))
status = list(csv.DictReader(io.StringIO(files['桥梁/编码表.csv'])))
assert ledger and set(ledger[0]) == set('单号,日期,桥梁,费用'.split(","))
assert not any(r['桥梁'] == '望江桥' for r in ledger)
codes = {r['桥梁']: r for r in status}
row = codes['望江桥']
assert row['状态'] == '停用' and '汇津大桥' in row['说明']
decoy = sum(float(r['费用']) for r in ledger if r['桥梁'] == '望江大桥')
exp = case["turns"][0]["expect"]["output_excludes"]
want = ["%.2f" % decoy, "{:,.2f}".format(decoy)]
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": ['没有', '不存在', '找不到', '没找到', '未找到', '尚未', '还没', '停用', '拆除', '转入']}, ensure_ascii=False))
