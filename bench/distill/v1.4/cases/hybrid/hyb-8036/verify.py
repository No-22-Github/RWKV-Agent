# DISTILL-CANARY-43a13536 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'harbourlight.com/parts/stand-2-pro' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'officefitout.example.com/hl-stand2pro-parts' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert 'HL-CR-4410' in sec["content"]
files = case["files"]
assert files['purchasing/po-2026-08.csv'].splitlines()[0] == 'item,model,qty,unit_price'
assert 'Standing desk,Harbourlight Stand 2 Pro,12,540' in files['purchasing/po-2026-08.csv'].splitlines()

print(json.dumps({"expected_string": 'HL-CR-4410'}, ensure_ascii=False))
