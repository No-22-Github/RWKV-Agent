# EXAM-CANARY-482ad1e6 : exam gap-fill case
import json, re
case = json.load(open("case.json", encoding="utf-8"))
prompt = case["turns"][0]["prompt"]
booked = int(re.search(r"预订(\d+)份", prompt).group(1))
added = int(re.search(r"另加(\d+)份", prompt).group(1))
left = int(re.search(r"剩(\d+)份", prompt).group(1))
staff = int(re.search(r"吃了(\d+)份", prompt).group(1))
print(json.dumps({"expected": booked + added - left - staff}))
