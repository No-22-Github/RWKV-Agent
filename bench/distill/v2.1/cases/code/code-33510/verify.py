# DISTILL-CANARY-638fa904 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f5078e42cadab63ca48b35d5341a3ee34f01351cb6fcf52b6f0cb2d731e6afec', "fixture changed"
import re
src = re.search(r'source (\S+)', files['tools/release.sh']).group(1)
lines = files[src].split(chr(10))
idx = [i for i, l in enumerate(lines, 1) if l.startswith('retry()')]
ans = src
assert idx == [17]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
