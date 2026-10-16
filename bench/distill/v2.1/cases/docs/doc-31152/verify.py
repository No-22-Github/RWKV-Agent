# DISTILL-CANARY-8b7759e6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'beec4f4203b4e9869ef5e1805ebe4b06de873d56f8cbc22281a0100c18b34f4b', "fixture changed"
def compute(files):
    return {"文档/说明.md": "# 安装说明\n\n1. 下载安装包\n2. 双击运行\n3. 点击完成\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
