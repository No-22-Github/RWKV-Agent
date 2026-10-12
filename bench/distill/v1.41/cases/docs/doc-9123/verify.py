# DISTILL-CANARY-4922d99c : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 26
assert all("终端" not in t for p, t in case["files"].items() if p != "手册/README.md")
assert case["files"]["手册/README.md"].startswith("# 手册说明")
assert case["files"]["手册/术语表.md"].startswith("# 术语表")
out = {}
for g in ["使用", "排错"]:
    path = "手册/%s.md" % g
    assert "客户端" in case["files"][path]
    out[path] = case["files"][path].replace("客户端", "终端")
assert "客户端" in case["files"]["手册/法务条款.md"]
print(json.dumps({"files": out}, ensure_ascii=False))
