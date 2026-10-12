# DISTILL-CANARY-e71a0131 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 41
assert case["files"]['财务/README.md'].startswith('# 财务表')
assert 'RMB-HK 是另一种币种' in case["files"]['财务/README.md']
FINAL = json.loads(r'''{"财务/2026-09.csv": "日期,金额,币种\n2026-09-04,6351.10,EUR\n2026-09-03,8697.10,CNY\n2026-09-09,4027.70,CNY\n2026-09-08,4854.80,USD\n2026-09-08,2219.30,RMB-HK\n2026-09-07,2633.70,EUR\n2026-09-16,6668.20,CNY\n2026-09-02,1639.90,CNY\n2026-09-20,8747.10,USD\n2026-09-25,8166.70,RMB-HK\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"财务/2026-07.csv": 1, "财务/2026-08.csv": 1, "财务/对外报表.csv": 1, "财务/模板.csv": 1, "财务/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
