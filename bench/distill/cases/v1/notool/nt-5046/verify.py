# DISTILL-CANARY-d7b059cb : distillation case
import json

case = json.load(open("case.json"))
centres = {}
for line in case["files"]["finance/cost-centre-register.txt"].splitlines():
    programme, code = [part.strip() for part in line.split("=")]
    centres[programme] = code
print(json.dumps({"expected_string": centres["cold chain retrofit"]}))
