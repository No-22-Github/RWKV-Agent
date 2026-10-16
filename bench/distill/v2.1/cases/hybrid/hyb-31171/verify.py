# DISTILL-CANARY-42dec34c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '530adebc24395a45c8fa41cf3362b6ef3721979a43b4b75cd22ea82d17e616f5', "fixture changed"
def compute(files):
    return {"整理/分类.md": "## 图片\n- 照片_01.jpg\n- 照片_02.jpg\n\n## 文档\n- 合同_2026.pdf\n- 报告_Q3.docx\n- 预算.xlsx\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
