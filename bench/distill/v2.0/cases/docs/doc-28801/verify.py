# DISTILL-CANARY-2cafacf2 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'场馆/寄存说明.md': '2e3aa0219eb8502a3bc604e39abe81f4120188fe632dfb3813ac942d931dd623', 'README.md': 'd5e4251025f00a71f7d393ed844b64a066ac4eb9859e1cd2cd4c1171cc6e15a4'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
line = [s for s in c["files"]['场馆/寄存说明.md'].splitlines() if s.strip()][-1]
separator = "=" if "=" in line else "：" if "：" in line else ":"
computed = line.split(separator, 1)[1].strip().strip('"')
for t in c["turns"]:
    assert t["expect"]["output_contains"] == [computed]
print(json.dumps({"expected_string": computed}, ensure_ascii=False))
