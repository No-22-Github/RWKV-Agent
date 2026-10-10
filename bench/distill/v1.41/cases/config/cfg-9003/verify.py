# DISTILL-CANARY-8f1de976 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["部署/说明.md"].startswith("# 部署" + chr(10)), "说明.md header"
assert "归档/ 下是下线服务的留档" in case["files"]["部署/说明.md"]
out = {}
for path, text in case["files"].items():
    if path.endswith("服务.env") and "/归档/" not in path:
        assert "日志级别=debug   # 上线前改回 info" in text, path
        out[path] = text.replace("日志级别=debug", "日志级别=info")
print(json.dumps({"files": out}, ensure_ascii=False))
