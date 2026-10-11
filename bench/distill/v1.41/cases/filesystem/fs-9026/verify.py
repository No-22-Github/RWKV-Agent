# DISTILL-CANARY-78d0edef : distillation case
import json, re
case = json.load(open("case.json"))
assert case["files"]["photos/README.txt"].startswith("Photo library notes.")
assert case["files"]["photos/2026/trip/contact-sheet.jpeg.txt"].startswith("contact sheet")
assert case["files"]["photos/2026/trip/already-ok.jpg"].startswith("jpg-bytes")
out = {}
for path, text in case["files"].items():
    m = re.fullmatch(r"(photos/(?:2026/trip|2026/family|2025))/(IMG_\d{4})\.jpeg", path)
    if m:
        assert text.startswith("jpeg-bytes " + m.group(2) + " "), path
        out[m.group(1) + "/" + m.group(2) + ".jpg"] = text
    elif path.endswith(".jpeg"):
        assert path.startswith("photos/raw/RAW_"), path
print(json.dumps({"files": out}))
