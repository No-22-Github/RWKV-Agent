# DISTILL-CANARY-ee6c7f5f : distillation case
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
content = case["files"]["部署清单.txt"]
page = next(e["content"] for e in case["web_fixture"] if "kunlunstack.example" in e.get("url", ""))
m = re.search(r"当前稳定版为\s*(v[0-9]+\.[0-9]+\.[0-9]+)", page)
if not m:
    raise SystemExit("stable version not found on the release page")
final = content.replace("v3.8.2", m.group(1))
if m.group(1) not in final:
    raise SystemExit("edit did not apply")
print(json.dumps({"files": {"部署清单.txt": final}}, ensure_ascii=False))
