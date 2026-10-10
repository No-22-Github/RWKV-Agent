# DISTILL-CANARY-2bf44932 : distillation case
import json
import re

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
offs = re.findall(r"UTC\+(\d+)", prompt)
base = int(re.search(r"It is (\d+):00", prompt).group(1))
hour = base + (int(offs[1]) - int(offs[0]))
assert hour == 14
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork studios")
print(json.dumps({"expected_contains_any": ["14:00", "2:00 PM", "2:00 pm", "2:00pm", "2 PM", "2 pm", "2pm"]}))
