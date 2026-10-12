# DISTILL-CANARY-280b6584 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 13
assert case["files"]["笔记/说明.md"].startswith("# 笔记说明")
assert "归档 里的文件名被别的程序按原名引用" in case["files"]["笔记/说明.md"]
assert case["files"]["笔记/工作/清单.txt.bak"].startswith("旧清单")
out = {}
for path, text in case["files"].items():
    if path.endswith(".txt") and "/归档/" not in path and "/草稿/" not in path:
        out[path[:-4] + ".md"] = text
print(json.dumps({"files": out}, ensure_ascii=False))
