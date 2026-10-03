# DISTILL-CANARY-3b6c50f4 : distillation case
import json

case = json.load(open("case.json"))
expr = case["turns"][0]["prompt"].split("`")[1].split()
minute, hour, dom, month, dow = expr
assert (minute, hour, dom, month, dow) == ("30", "2", "*", "*", "1-5")
words = ["Monday through Friday", "Monday to Friday", "Monday-Friday", "weekday", "Mon-Fri", "Mon\u2013Fri", "Monday\u2013Friday"]
print(json.dumps({"expected_contains_any": words}))
