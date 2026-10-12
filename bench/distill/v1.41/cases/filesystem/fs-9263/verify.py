# DISTILL-CANARY-5ea3369d : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 14
assert case["files"]['文档站/README.md'].startswith('# 文档站')
assert '发布镜像 是同步给外部站点的只读副本' in case["files"]['文档站/README.md']
FINAL = json.loads(r'''{"文档站/指南/安装.md": "安装步骤\n", "文档站/参考/接口.md": "接口说明\n", "文档站/参考/术语.md": "术语说明\n", "文档站/博客/发布说明.md": "新版本发布\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"文档站/指南/导入.markdown": 1, "文档站/指南/导出.markdown": 1, "文档站/发布镜像/安装.markdown": 1, "文档站/发布镜像/接口.markdown": 1, "文档站/参考/变更.md": 1, "文档站/参考/旧笔记.markdown.bak": 1, "文档站/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
