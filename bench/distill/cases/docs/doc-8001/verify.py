# DISTILL-CANARY-fa877867 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith("规范/ 只放已发布的正式版本")
log = files["规范/修订记录.md"]
rows = [l for l in log.splitlines() if l.startswith("| 冷库作业规范")]
status = {r.split("|")[2].strip(): r.split("|")[3].strip() for r in rows}
assert status["第三版"] == "起草中" and status["第二版"].startswith("已发布")
assert not any("冷库作业规范-第三版" in p for p in files)
# The only third-edition text is the transport standard, whose 冷藏品 band is the decoy.
transport = files["规范/冷链运输规范-第三版.md"]
assert re.search(r"冷藏品车厢 2℃ 至 6℃", transport)
words = ["起草", "未发布", "没有发布", "尚未发布", "还没发布", "未定稿", "没有定稿"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
