# DISTILL-CANARY-72041546 : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://pinecone-editor.org/download/changelog'][0]["content"]
m = re.search('## (\\d+\\.\\d+\\.\\d+)（稳定版，2026-09-24）', off)
assert m and m.group(1) == '2.9.0'
print(json.dumps({"expected_contains_any": ["2.9.0"]}, ensure_ascii=False))
