# DISTILL-CANARY-128b1990 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 28
assert case["files"]['日志轮转/README.md'].startswith('# 日志轮转')
assert 'maxage 是保留天数' in case["files"]['日志轮转/README.md']
FINAL = json.loads(r'''{"日志轮转/网关.conf": "path /var/log/网关/*.log\nrotate 14\nmaxage 7\ncompress\n", "日志轮转/订单.conf": "path /var/log/订单/*.log\nrotate 14\nmaxage 7\ncompress\n", "日志轮转/支付.conf": "path /var/log/支付/*.log\nrotate 30\nmaxage 7\ncompress\n", "日志轮转/认证.conf": "path /var/log/认证/*.log\nrotate 30\nmaxage 7\ncompress\n", "日志轮转/搜索.conf": "path /var/log/搜索/*.log\nrotate 14\nmaxage 7\ncompress\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"日志轮转/_停用/旧任务.conf": 1, "日志轮转/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
