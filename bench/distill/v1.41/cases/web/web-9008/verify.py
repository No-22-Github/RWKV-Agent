# DISTILL-CANARY-37ca9778 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["runbooks/vendors.md"].startswith("# Vendors")
assert "status.quillmesh.io/api/v2/summary.json" in case["files"]["runbooks/vendors.md"]
page = json.loads(case["web_fixture"][0]["content"])
bad = [c["name"] for c in page["components"] if c["status"] != "operational"]
assert len(bad) == 1
print(json.dumps({"expected_string": bad[0]}))
