# DISTILL-CANARY-fedba7ce : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 23
assert case["files"]['脚本集/README.md'].startswith('# 脚本集')
assert 'lib 里是被 source 的片段' in case["files"]['脚本集/README.md']
FINAL = json.loads(r'''{"脚本集/备份.sh": "#!/bin/sh\nset -eu\n# 备份任务\necho \"备份 开始\"\n", "脚本集/同步.sh": "#!/bin/sh\nset -eu\n# 同步任务\necho \"同步 开始\"\n", "脚本集/发布.sh": "#!/bin/sh\nset -eu\n# 发布任务\necho \"发布 开始\"\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"脚本集/清理.sh": 1, "脚本集/巡检.sh": 1, "脚本集/lib/log.sh": 1, "脚本集/lib/net.sh": 1, "脚本集/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
