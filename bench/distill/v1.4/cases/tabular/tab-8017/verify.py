# DISTILL-CANARY-9d038f73 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files['配送/2026-09.csv'].splitlines()[0] == '日期,配送点,件数'
assert files['配送点/名录.csv'].splitlines()[0] == '编码,配送点,状态,说明'
ledger = list(csv.DictReader(io.StringIO(files['配送/2026-09.csv'])))
status = list(csv.DictReader(io.StringIO(files['配送点/名录.csv'])))
assert ledger and set(ledger[0]) == set('日期,配送点,件数'.split(","))
assert not any(r['配送点'] == '城南配送点' for r in ledger)
codes = {r['配送点']: r for r in status}
row = codes['城南配送点']
assert row['状态'] == '停用' and '中央配送点' in row['说明']
decoy = sum(float(r['件数']) for r in ledger if r['配送点'] == '城西配送点')
exp = case["turns"][0]["expect"]["output_excludes"]
n = int(round(decoy))
want = [str(n), "{:,}".format(n)]
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": ['没有', '不存在', '找不到', '没找到', '未找到', '尚未', '还没', '停用', '并入', '合并']}, ensure_ascii=False))
