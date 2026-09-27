# DISTILL-CANARY-47e0a95b : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][1]["prompt"]


def number(pattern):
    m = re.search(pattern, prompt)
    assert m, "prompt is missing " + pattern
    return int(m.group(1).replace(",", ""))


morning = number(r"([0-9]+) people were there in the morning")
afternoon = number(r"and ([0-9]+) in the afternoon")
both = number(r"and ([0-9]+) of the morning group")
print(json.dumps({"expected_number": morning + afternoon - both}))
