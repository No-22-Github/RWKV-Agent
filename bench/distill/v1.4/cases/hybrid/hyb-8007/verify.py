# DISTILL-CANARY-9d5e421a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith('# 洄澜潜水')
rows = list(csv.DictReader(io.StringIO(files['装备室/送检清单.csv'])))
assert rows and set(rows[0]) == set(['材质', '状态', '瓶号'])
pages = {w["url"]: w for w in case["web_fixture"]}
official = [w for w in case["web_fixture"] if 'wuyu-test.cn/price' in w["url"]][0]
assert official.get("error") and official["error"].startswith('Connection timed out')
words = ['503', '打不开', '无法访问', '访问不了', '访问失败', '抓取失败', '获取失败', '没能获取', '没有获取', '无法获取', '没法获取', '没能打开', '没法打开', '打开失败', '加载失败', '无法加载', '超时', '连接超时', '连不上', '没能连上', '拿不到', '取不到', '没能核实', '没有核实', '无法核实', '没法核实', '没能确认', '无法确认', '未能确认']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
