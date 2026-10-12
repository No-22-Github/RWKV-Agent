# DISTILL-CANARY-ddf26023 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 52
assert case["files"]['项目/README.md'].startswith('# 项目依赖')
assert 'axios-retry 由平台组统一管理' in case["files"]['项目/README.md']
FINAL = json.loads(r'''{"项目/商城/package.json": "{\n  \"name\": \"商城\",\n  \"dependencies\": {\n    \"axios\": \"1.6.2\",\n    \"axios-retry\": \"0.21.1\",\n    \"lodash\": \"4.17.21\"\n  }\n}\n", "项目/报表/package.json": "{\n  \"name\": \"报表\",\n  \"dependencies\": {\n    \"axios\": \"1.6.2\",\n    \"axios-retry\": \"0.21.1\",\n    \"lodash\": \"4.17.21\"\n  }\n}\n", "项目/小程序/package.json": "{\n  \"name\": \"小程序\",\n  \"dependencies\": {\n    \"axios\": \"1.6.2\",\n    \"axios-retry\": \"0.21.1\",\n    \"lodash\": \"4.17.21\"\n  }\n}\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"项目/后台/package.json": 1, "项目/结算/package.json": 1, "项目/_vendored/package.json": 1, "项目/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
