# DISTILL-CANARY-1eed8d0b : distillation case
import json
import re

case = json.load(open("case.json"))
log = case["files"]['logs/醒发间/2026-09-12.log'].splitlines()
assert log[0].startswith('# 醒发间温湿度记录')
stamps = [re.match(r"2026-09-12T(\d\d):(\d\d)", l) for l in log[1:]]
minutes = [int(m.group(1)) * 60 + int(m.group(2)) for m in stamps]
assert not any(120 <= x < 180 for x in minutes)
assert any('暂停记录' in l for l in log) and any('不会补录' in l for l in log)
words = ['中断', '暂停', '维护', '没有采集', '没有推送', '没有日志', '缺失', '空白', '没有记录', '停机', '无法确定', '无法统计', '没有任何记录', '一条记录都没有', '不会补传', '不补录']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
