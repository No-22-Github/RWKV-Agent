# DISTILL-CANARY-616db5da : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd88904dcc4fdff184c857a1d7a054342675f368d09b82105147a96f88b73ad52', "fixture changed"
import re
m = re.search(r"from '\./([\w-]+\.js)'", files['src/player.js'])
ans = 'src/' + m.group(1)
assert files[ans].split(chr(10))[16].startswith('export const FADE_STEP_MS = ')

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
