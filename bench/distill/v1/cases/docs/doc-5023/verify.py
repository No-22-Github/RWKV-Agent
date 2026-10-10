# DISTILL-CANARY-e5138bd0 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["checklist.txt"].splitlines()

# The checklist carries two headings; the items under the first one are the
# ones an applicant brings to the interview.
start = lines.index("Items to hand in at the interview") + 1
end = next(i for i in range(start, len(lines)) if lines[i].startswith("Items to hand in"))
print(json.dumps({"expected_number": end - start}))
