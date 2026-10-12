# DISTILL-CANARY-c401cf3c : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 14
assert case["files"]['etc/README.md'].startswith('# etc')
assert 'etc/readonly is mounted from the image' in case["files"]['etc/README.md']
FINAL = json.loads(r'''{}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"etc/app.cfg": 1, "etc/db.cfg": 1, "etc/cache.cfg": 1, "etc/net/proxy.cfg": 1, "etc/net/dns.cfg": 1, "etc/legacy/mailer.cfg": 1, "etc/legacy/ftp.cfg": 1, "etc/readonly/base.cfg": 1, "etc/readonly/os.cfg": 1, "etc/old.cfg.bak": 1, "etc/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
