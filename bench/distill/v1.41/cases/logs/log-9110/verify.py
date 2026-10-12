# DISTILL-CANARY-fbec4fc0 : distillation case
import json
case = json.load(open("case.json"))
rows = case["files"]["接口监控/latency.log"].splitlines()
assert str(len(rows)) in case["files"]["接口监控/口径.md"]
best = []
for row in rows:
    parts = row.split(" ")
    assert len(parts) == 4 and parts[1].startswith("路由=") and parts[3].startswith("耗时=") and parts[3].endswith("ms"), row
    if parts[1] == "路由=/v2/refund":
        best.append(int(parts[3][3:-2]))
assert best.count(max(best)) == 1
print(json.dumps({"expected_contains_any": [str(max(best))]}))
