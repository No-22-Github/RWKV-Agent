# DISTILL-CANARY-779c38b4 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 27
assert case["files"]['微服务/README.md'].startswith('# 微服务配置')
assert '_样例 是新服务的复制模板' in case["files"]['微服务/README.md']
FINAL = json.loads(r'''{"微服务/订单/conf.yaml": "name: 订单\nretries: 3\ntimeout: 30\n", "微服务/支付/conf.yaml": "name: 支付\nretries: 3\ntimeout: 30\n", "微服务/库存/conf.yaml": "name: 库存\nretries: 3\ntimeout: 30\n", "微服务/通知/conf.yaml": "name: 通知\nretries: 3\ntimeout: 30\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"微服务/物流/conf.yaml": 1, "微服务/风控/conf.yaml": 1, "微服务/搜索/conf.yaml": 1, "微服务/_样例/conf.yaml": 1, "微服务/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
want = sorted(p.split("/")[1] for p, t in state.items() if p.endswith("conf.yaml") and "retries: 3" not in t.splitlines())
assert want == ["_样例", "物流", "风控"], want
print(json.dumps({"expected_string": "风控"}, ensure_ascii=False))
