# DISTILL-CANARY-00f25196 : distillation case
import json
import re

case = json.load(open("case.json"))
log = case["files"]['logs/告警平台/2026-09-20.log'].splitlines()
assert log[0].startswith('# 漏水告警平台日志')
stamps = [re.match(r"2026-09-20T(\d\d):(\d\d)", l) for l in log[1:]]
minutes = [int(m.group(1)) * 60 + int(m.group(2)) for m in stamps]
assert not any(180 <= x < 240 for x in minutes)
assert any('暂停入库' in l for l in log) and any('不会补传' in l for l in log)
words = ['中断', '暂停', '维护', '没有采集', '没有推送', '没有日志', '缺失', '空白', '没有记录', '停机', '无法确定', '无法统计', '没有任何记录', '一条记录都没有', '不会补传', '不补录']
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
