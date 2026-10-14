# DISTILL-CANARY-b36638f4 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '21cba371ef0f0cfa13a24d7217bfd788b36a4c19c0c1705365907193fb3b7c2c', "fixture changed"
m = re.search('(li\\.zong@[\\w.]+)', case["files"]['contacts.csv'])
assert m and m.group(1) == 'li.zong@lanting.example'
draft = '收件人：li.zong@lanting.example\n主题：客户拜访时间调整\n\n李总好，下周二的客户拜访改到上午十点，请确认。\n'
assert all(s in draft for s in ['li.zong@lanting.example', '十点'])
print(json.dumps({"files": {'邮件草稿.md': draft}}, ensure_ascii=False))
