# DISTILL-CANARY-ff036db5 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 22
assert case["files"]['部署/README.md'].startswith('# 部署清单')
assert 'mirror 行' in case["files"]['部署/README.md']
FINAL = json.loads(r'''{}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"部署/订单.yaml": 1, "部署/支付.yaml": 1, "部署/对账.yaml": 1, "部署/搜索.yaml": 1, "部署/通知.yaml": 1, "部署/_样例.yaml": 1, "部署/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
