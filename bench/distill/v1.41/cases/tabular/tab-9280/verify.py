# DISTILL-CANARY-9d9bdfd8 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 34
assert case["files"]['客户/README.md'].startswith('# 客户表')
assert '「备用手机」是另一列' in case["files"]['客户/README.md']
FINAL = json.loads(r'''{}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"客户/华北.csv": 1, "客户/华东.csv": 1, "客户/华南.csv": 1, "客户/西南.csv": 1, "客户/导出模板.csv": 1, "客户/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
