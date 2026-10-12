# DISTILL-CANARY-a5779a9c : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 28
assert case["files"]['文档/README.md'].startswith('# 文档说明')
assert '更新日志.md 是历史记录' in case["files"]['文档/README.md']
FINAL = json.loads(r'''{"文档/入门.md": "# 入门\n\n安装扩展后重启应用。\n扩展列表在设置里。\n", "文档/进阶.md": "# 进阶\n\n编写扩展需要实现两个接口。\n", "文档/FAQ.md": "# FAQ\n\n问：扩展装不上怎么办？\n答：检查版本。\n", "文档/发布.md": "# 发布\n\n扩展市场每周更新。\n", "文档/迁移.md": "# 迁移\n\n旧版扩展需要重新打包。\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"文档/术语表.md": 1, "文档/更新日志.md": 1, "文档/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
want = sorted(p.split("/")[1][:-3] for p, t in state.items() if "插件" in t)
assert want == sorted(["README", "术语表", "更新日志"]), want
print(json.dumps({"expected_string": "术语表"}, ensure_ascii=False))
