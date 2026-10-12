# DISTILL-CANARY-175b101c : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 28
assert case["files"]["编排/README.md"].startswith("# 编排配置")
assert "minReplicas 是保底副本数" in case["files"]["编排/README.md"]
want = {"网关": 4, "订单": 6, "报表": 2, "搜索": 4, "通知": 4}
out = {}
for n, k in want.items():
    path = "编排/" + n + "/deploy.yaml"
    rows = case["files"][path].splitlines()
    assert rows[0] == "name: " + n and rows[1] == "replicas: 2" and rows[2] == "minReplicas: 2", path
    out[path] = case["files"][path].replace("\nreplicas: 2\n", "\nreplicas: %d\n" % k)
assert case["files"]["编排/_样例/deploy.yaml"].splitlines()[1] == "replicas: 2"
print(json.dumps({"files": out}, ensure_ascii=False))
