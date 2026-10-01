# DISTILL-CANARY-1d545c2b : distillation case
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
content = case["files"]["应急预案.txt"]
page = next(e["content"] for e in case["web_fixture"] if "forum.citylife.example" in e.get("url", ""))
m = re.search(r"24\s*小时值班电话调整为\s*([0-9\-]+)", page)
if not m:
    raise SystemExit("duty phone change not found in the reposted notice")
final = content.replace("0755-26631188", m.group(1))
if m.group(1) not in final:
    raise SystemExit("edit did not apply")
print(json.dumps({"files": {"应急预案.txt": final}}, ensure_ascii=False))
