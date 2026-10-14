# DISTILL-CANARY-13dcd303 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '54f6f8db8b725134fe2c0a9b13a94371ff167615a2ad173ad3fef88b9c2a9d11', "fixture changed"
m = re.search('Northwind Traders - AP contact: ([\\w.@]+)', case["files"]['vendors.md'])
assert m and m.group(1) == 'ap@northwind.example'
m = re.search('read (PO-\\d+)', case["files"]['po-note.md'])
assert m and m.group(1) == 'PO-55820'
print(json.dumps({"expected_string": 'ap@northwind.example'}, ensure_ascii=False))
