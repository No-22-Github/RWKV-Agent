# DISTILL-CANARY-15d7b8a2 : distillation case
import json
import re

case = json.load(open("case.json"))

# Each revision says the date from which it applies; the governing revision is
# the one whose date is the latest of those that have taken effect.
def applies_from(text):
    line = next(l for l in text.splitlines() if "brews made on or after" in l)
    match = re.search(r"on or after (\d+) (\w+) (\d+)", line)
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return (int(match.group(3)), months.index(match.group(2)) + 1, int(match.group(1)))


sheets = {}
for path, text in case["files"].items():
    if "/water-treatment-" not in path:
        continue
    revision = int(re.search(r"revision (\d+)", text).group(1))
    sheets[revision] = applies_from(text)

governing = max(sheets, key=lambda revision: sheets[revision])
print(json.dumps({"expected_number": governing}))
