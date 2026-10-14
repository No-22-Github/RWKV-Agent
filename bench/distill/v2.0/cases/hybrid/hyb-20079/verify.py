# DISTILL-CANARY-abbcef65 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '03dda13ea08079cf5552b7925a63f2ba75c7718b9125aa0448deb4baa2b73449', "fixture changed"
m = re.search('(zhao\\.liang@[\\w.]+)', case["files"]['contacts.csv'])
assert m and m.group(1) == 'zhao.liang@lanting.example'
draft = '收件人：zhao.liang@lanting.example\n\n赵亮，今晚的发布推迟到明早九点。\n'
assert all(s in draft for s in ['zhao.liang@lanting.example', '明早九点'])
print(json.dumps({"files": {'邮件草稿.md': draft}}, ensure_ascii=False))
