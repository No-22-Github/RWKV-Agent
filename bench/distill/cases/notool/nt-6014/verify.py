# DISTILL-CANARY-f29d3c86 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return int(m.group(1).replace(",", ""))


morning = number(r"([0-9]+) joined the morning broadcast")
evening = number(r"and ([0-9]+) the evening rerun")
both = number(r"and ([0-9]+) of the morning viewers")
print(json.dumps({"expected_number": morning + evening - both}))
