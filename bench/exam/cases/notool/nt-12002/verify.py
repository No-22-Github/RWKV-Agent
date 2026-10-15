# EXAM-CANARY-c81f530d : exam gap-fill case
import json, re
from decimal import Decimal
case = json.load(open("case.json", encoding="utf-8"))
prompt = case["turns"][0]["prompt"]
size = Decimal(re.search(r"共([\d.]+) GiB", prompt).group(1))
count = Decimal(re.search(r"分成(\d+)包", prompt).group(1))
factor = Decimal(re.search(r"1 GiB = (\d+) MiB", prompt).group(1))
print(json.dumps({"expected": float(size * factor / count)}))
