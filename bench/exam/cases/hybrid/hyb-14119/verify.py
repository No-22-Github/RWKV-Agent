# EXAM-CANARY-a1dbfd87 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
nj = sum(1 for k in files if k.startswith("相册/2026夏/") and k.endswith(".jpg"))
np_ = sum(1 for k in files if k.startswith("相册/2026夏/") and k.endswith(".png"))
text = files["相册/统计.md"].replace("- jpg: ", "- jpg: %d" % nj).replace("- png: ", "- png: %d" % np_)
print(json.dumps({"expected_number": nj + np_, "files": {"相册/统计.md": text}}))
