# DISTILL-CANARY-ac0fd162 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files['入库/2026-09.csv'].splitlines()[0] == '日期,冷库,扎数'
assert files['冷库/编码表.csv'].splitlines()[0] == '编码,冷库,状态,说明'
ledger = list(csv.DictReader(io.StringIO(files['入库/2026-09.csv'])))
status = list(csv.DictReader(io.StringIO(files['冷库/编码表.csv'])))
assert ledger and set(ledger[0]) == set('日期,冷库,扎数'.split(","))
assert not any(r['冷库'] == '3号冷库' for r in ledger)
codes = {r['冷库']: r for r in status}
row = codes['3号冷库']
assert row['状态'] == '停用' and '1号冷库' in row['说明']
decoy = sum(float(r['扎数']) for r in ledger if r['冷库'] == '13号冷库')
exp = case["turns"][0]["expect"]["output_excludes"]
n = int(round(decoy))
want = [str(n), "{:,}".format(n)]
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": ['没有', '不存在', '找不到', '没找到', '未找到', '尚未', '还没', '停用', '拆除', '并入']}, ensure_ascii=False))
