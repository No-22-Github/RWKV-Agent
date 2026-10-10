# DISTILL-CANARY-7c98c6c4 : distillation case
import json

case = json.load(open("case.json"))
forms = {}
for line in case["files"]["registry/forms-index.txt"].splitlines():
    name, number = [part.strip() for part in line.split("->")]
    forms[name] = number
print(json.dumps({"expected_string": forms["late withdrawal petition"]}))
