# DISTILL-CANARY-dce01d59 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["服务/README.md"].startswith("# 服务配置" + chr(10))
assert "mirror.registry.host 是镜像源" in case["files"]["服务/README.md"]
out = {}
for path, text in case["files"].items():
    if not path.endswith("app.properties") or "/_模板/" in path:
        continue
    rows = text.splitlines()
    assert rows[0].startswith("name=") and rows[1] == "registry.host=reg-old.corp", path
    assert rows[2] == "mirror.registry.host=reg-old.corp", path
    if "/支付/" not in path:
        out[path] = text.replace(chr(10) + "registry.host=reg-old.corp" + chr(10), chr(10) + "registry.host=reg.corp" + chr(10))
print(json.dumps({"files": out}, ensure_ascii=False))
