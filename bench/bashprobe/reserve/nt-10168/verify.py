# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e8735c7247cef237be584d90782d4b04cbc77c942cb1b7a2aa1e5d99921ce255', "fixture changed"
print(json.dumps({"expected_contains_any": ["chmod +x", "chmod u+x", "chmod 755", "chmod 744"]}, ensure_ascii=False))
