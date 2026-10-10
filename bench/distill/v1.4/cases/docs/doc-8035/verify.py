# DISTILL-CANARY-b162c398 : distillation case
import json
import re

NAMES = ["一", "二", "三", "四", "五", "六", "日"]
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
base = NAMES.index(re.search(r"今天是周(.)", prompt).group(1))
shift = int(re.search(r"(\d+) 天后", prompt).group(1))
idx = (base + shift) % 7
assert idx == 0
assert case["files"]["README.md"].splitlines()[0].startswith("# 麦丰面点坊 会员活动")
if idx == 6:
    words = ["周日", "星期日", "星期天", "礼拜天", "礼拜日"]
else:
    words = ["周" + NAMES[idx], "星期" + NAMES[idx], "礼拜" + NAMES[idx]]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
