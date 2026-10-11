# DISTILL-CANARY-46f51885 : distillation case
import hashlib, json
c = json.load(open("case.json"))
for p, h in {'包装/覆膜.yaml': '0b52330afda729506224e3d6af88b586dbff3693301edb8ae44fff2f4b0ea301', 'README.md': 'd5e4251025f00a71f7d393ed844b64a066ac4eb9859e1cd2cd4c1171cc6e15a4'}.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
line = [s for s in c["files"]['包装/覆膜.yaml'].splitlines() if s.strip()][-1]
separator = "=" if "=" in line else "：" if "：" in line else ":"
computed = line.split(separator, 1)[1].strip().strip('"')
for t in c["turns"]:
    assert t["expect"]["output_contains"] == [computed]
print(json.dumps({"expected_string": computed}, ensure_ascii=False))
