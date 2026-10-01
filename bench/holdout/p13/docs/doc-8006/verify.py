# DISTILL-CANARY-b64c19e0 : p13 holdout (eval-only)
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
doc = case["files"]["docs/onboarding.md"]
notice = case["files"]["notices/vpn-rename-2026-09.md"]
new_name = re.search(r"renamed\s+(\S+)", notice).group(1)
assert "contractors-vpn" in doc
print(json.dumps({"files": {
    "docs/onboarding.md": doc.replace("contractors-vpn", new_name),
    "notices/vpn-rename-2026-09.md": notice,
}}))
