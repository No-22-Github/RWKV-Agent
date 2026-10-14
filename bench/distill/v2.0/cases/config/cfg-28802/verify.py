# DISTILL-CANARY-4f93e9f2 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'灯光/台控.toml': '423f68ad18c1a30ff3fe0e2ff93f2b01e853c4fbbe48f85d5c36adb546482a03', 'README.md': 'd5e4251025f00a71f7d393ed844b64a066ac4eb9859e1cd2cd4c1171cc6e15a4'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
line = [s for s in c["files"]['灯光/台控.toml'].splitlines() if s.strip()][-1]
separator = "=" if "=" in line else "：" if "：" in line else ":"
computed = line.split(separator, 1)[1].strip().strip('"')
for t in c["turns"]:
    assert t["expect"]["output_contains"] == [computed]
print(json.dumps({"expected_string": computed}, ensure_ascii=False))
