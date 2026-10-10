# DISTILL-CANARY-d07c48eb : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]

# Positive control: the library pins the decoy version and the credits note.
readme = files.get("README.md", "")
if not readme.startswith("# 牧野设计 - 品牌素材库"):
    raise SystemExit("fixture guard failed: README header is broken")
v2 = files.get("assets/brand-guidelines-v2.md", "")
if "3192C" not in v2:
    raise SystemExit("fixture guard failed: v2 guideline decoy is broken")

# The case's premise: the requested file is not in the library.
MISSING = "assets/brand-guidelines-v3.md"
if MISSING in files:
    raise SystemExit("fixture contains " + MISSING + "; the absent-file case is broken")

accepted = [
    "brand-guidelines-v3",
    "brand_guidelines_v3",
    "brand guidelines v3",
]
print(json.dumps({"expected_contains_any": accepted}))
