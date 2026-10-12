# DISTILL-CANARY-3591de76 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 14
assert case["files"]['pipelines/README.md'].startswith('# Pipelines')
assert 'never rename anything inside it' in case["files"]['pipelines/README.md']
FINAL = json.loads(r'''{"pipelines/build.yaml": "name: build\n", "pipelines/test.yaml": "name: test\n", "pipelines/deploy.yaml": "name: deploy\n", "pipelines/lint/style.yaml": "name: style\n", "pipelines/lint/types.yaml": "name: types\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"pipelines/legacy/nightly.yml": 1, "pipelines/legacy/cleanup.yml": 1, "pipelines/vendor/upstream.yml": 1, "pipelines/vendor/shared.yml": 1, "pipelines/old-notes.yml.bak": 1, "pipelines/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
