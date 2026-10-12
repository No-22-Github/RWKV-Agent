# DISTILL-CANARY-ee082e66 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["文档/README.md"].startswith("# 文档说明")
def migrate(text):
    out = []
    inside = False
    for line in text.splitlines(keepends=True):
        if "历史:开始" in line:
            inside = True
        out.append(line if inside else line.replace("星桥 1.8", "星桥 2.0"))
        if "历史:结束" in line:
            inside = False
    return "".join(out)
out = {}
for path, text in case["files"].items():
    if path.endswith("README.md") or path.endswith("更新记录.md"):
        continue
    assert text.startswith("# "), path
    assert "<!-- 历史:开始 -->" not in text or "<!-- 历史:结束 -->" in text, path
    out[path] = migrate(text)
print(json.dumps({"files": out}, ensure_ascii=False))
