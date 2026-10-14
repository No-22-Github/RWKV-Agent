# DISTILL-CANARY-b23d5bdb : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
minute, hour, dom, month, dow = prompt.split("`")[1].split()
assert (minute, hour, dom, month, dow) == ("0", "22", "*", "*", "0")
assert case["files"]["README.md"].splitlines()[0].startswith("# Loomwork back office")
print(json.dumps({"expected_contains_any": ["22:00", "10 PM", "10 pm", "10pm", "10:00 PM", "10:00 pm"]}))
