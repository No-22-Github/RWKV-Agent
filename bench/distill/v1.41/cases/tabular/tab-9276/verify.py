# DISTILL-CANARY-87ab6980 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 43
assert case["files"]['库存/README.md'].startswith('# 库存表')
assert '「件套」是另一种单位' in case["files"]['库存/README.md']
FINAL = json.loads(r'''{"库存/2026-07.txt": "货号,品名,数量,单位\nS0701,货品57,37,个\nS0702,货品12,32,个\nS0703,货品93,55,个\nS0704,货品70,62,个\nS0705,货品22,59,个\nS0706,货品38,36,个\nS0707,货品24,87,箱\nS0708,货品67,68,个\nS0709,货品47,22,件套\nS0710,货品20,18,个\nS0711,货品21,65,个\nS0712,货品12,22,个\nS0713,货品35,25,个\n", "库存/2026-09.txt": "货号,品名,数量,单位\nS0901,货品79,21,个\nS0902,货品52,41,件套\nS0903,货品42,70,个\nS0904,货品53,41,个\nS0905,货品71,89,个\nS0906,货品38,26,箱\nS0907,货品93,36,个\nS0908,货品21,47,件套\nS0909,货品35,40,个\nS0910,货品46,90,件套\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"库存/2026-08.txt": 1, "库存/模板.txt": 1, "库存/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
n = sum(1 for p, t in state.items() if p.startswith("库存/2026-") for r in t.splitlines() if r.endswith(",个"))
assert n == 22, n
print(json.dumps({"expected_contains_any": [str(n)]}))
