# DISTILL-CANARY-8f0d47ab : distillation case
import json
import re

case = json.load(open("case.json"))

# Each issue says the date from which it applies; the governing issue is the one
# whose date is the latest of those that have taken effect.
def applies_from(text):
    line = next(l for l in text.splitlines() if "applies to work carried out on or after" in l
                or "applied to work carried out on or after" in l)
    match = re.search(r"on or after (\d+) (\w+) (\d+)", line)
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return (int(match.group(3)), months.index(match.group(2)) + 1, int(match.group(1)))


sheets = {}
for path, text in case["files"].items():
    if "/weld-params-" not in path:
        continue
    issue = int(re.search(r"issue (\d+)", text).group(1))
    sheets[issue] = applies_from(text)

governing = max(sheets, key=lambda issue: sheets[issue])
print(json.dumps({"expected_number": governing}))
