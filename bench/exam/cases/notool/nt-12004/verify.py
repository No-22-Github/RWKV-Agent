# EXAM-CANARY-f42d670a : sol pilot case
import json,re
case=json.load(open("case.json",encoding="utf-8"))
prompt=case["turns"][0]["prompt"]
number=re.search(r"电话\s*(\d{11})",prompt).group(1)
request={"action":"phone_call" if "拨电话" in prompt else "other","number":number}
print(json.dumps({"request":request},ensure_ascii=False))
