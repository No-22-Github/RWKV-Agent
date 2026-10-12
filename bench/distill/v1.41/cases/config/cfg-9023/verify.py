# DISTILL-CANARY-57d812d7 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["部署/README.md"].startswith("# 部署说明")
total = 0
count = 0
for path, text in case["files"].items():
    if not path.endswith("values.yaml"):
        continue
    count += 1
    rows = text.splitlines()
    assert len(rows) == 4 and rows[0].startswith("服务: ") and rows[1].startswith("环境: "), path
    assert rows[2].startswith("副本数: ") and rows[3].startswith("备用副本数: "), path
    if rows[1] == "环境: prod":
        total += int(rows[2].split(": ")[1])
assert count == 40
print(json.dumps({"expected_number": total}))
