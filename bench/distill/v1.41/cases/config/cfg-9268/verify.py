# DISTILL-CANARY-8f439719 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 29
assert case["files"]['services/README.md'].startswith('# Services')
assert '_base is the shared base image' in case["files"]['services/README.md']
FINAL = json.loads(r'''{"services/api/Dockerfile": "FROM node:20-alpine\nWORKDIR /app\nCOPY . .\nRUN npm ci\nCMD [\"node\", \"server.js\"]\n", "services/web/Dockerfile": "FROM node:20-alpine\nWORKDIR /app\nCOPY . .\nRUN npm ci\nCMD [\"node\", \"server.js\"]\n", "services/worker/Dockerfile": "FROM node:20-alpine\nWORKDIR /app\nCOPY . .\nRUN npm ci\nCMD [\"node\", \"server.js\"]\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"services/reports/Dockerfile": 1, "services/exporter/Dockerfile": 1, "services/_base/Dockerfile": 1, "services/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
