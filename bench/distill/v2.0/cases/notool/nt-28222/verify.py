# DISTILL-CANARY-c7ad693b : distillation case
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
from fractions import Fraction
assert Fraction(3, 4) + Fraction(5, 8) == Fraction(11, 8)
print(json.dumps({"expected_contains_any": ['11/8', '1又3/8', '1 又 3/8', '1.375', '1 3/8', '八分之十一']}, ensure_ascii=False))
