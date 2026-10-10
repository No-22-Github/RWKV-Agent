# DISTILL-CANARY-b96fea3d : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith("Guest-laundry care documents")
chart = files["docs/stain-chart.md"]
rows = [l for l in chart.splitlines() if l.startswith("## ")]
assert "## Silk" not in rows
assert "## Satin" in rows and "no silk row" in chart
guide = files["docs/vendor-guide-extract.md"]
assert "Silk" in guide and "vendor" in guide
words = ["not covered", "not listed", "no row", "no entry", "isn't covered", "routed", "outside the chart", "specialist"]
print(json.dumps({"expected_contains_any": words}))
