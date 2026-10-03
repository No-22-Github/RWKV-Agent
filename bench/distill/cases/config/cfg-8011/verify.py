# DISTILL-CANARY-a8c49d58 : distillation case
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("可用容量")
c = {}
for l in case["files"]["配置/存储集群.yaml"].splitlines():
    k, v = l.split(":", 1)
    c[k.strip()] = v.split("#")[0].strip()
assert c["集群"] == "澄江对象存储"
v = int(c["节点数"]) * int(c["每节点盘数"]) * float(c["单盘容量TB"]) / int(c["副本数"]) * (1 - float(c["预留比例"]))
print(json.dumps({"expected_number": round(v, 1)}))
