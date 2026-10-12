# DISTILL-CANARY-7d6eb4b3 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 28
assert case["files"]['config/README.md'].startswith('# Service env files')
assert 'API_BASE_LEGACY keeps pointing at v1' in case["files"]['config/README.md']
FINAL = json.loads(r'''{"config/web.env": "APP_NAME=web\nAPI_BASE=https://api-v2.corp.io\nAPI_BASE_LEGACY=https://api-v1.corp.io\nTIMEOUT=30\n", "config/mobile.env": "APP_NAME=mobile\nAPI_BASE=https://api-v2.corp.io\nAPI_BASE_LEGACY=https://api-v1.corp.io\nTIMEOUT=30\n", "config/admin.env": "APP_NAME=admin\nAPI_BASE=https://api-v2.corp.io\nAPI_BASE_LEGACY=https://api-v1.corp.io\nTIMEOUT=30\n", "config/jobs.env": "APP_NAME=jobs\nAPI_BASE=https://api-v2-eu.corp.io\nAPI_BASE_LEGACY=https://api-v1.corp.io\nTIMEOUT=30\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"config/billing.env": 1, "config/example.env": 1, "config/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
