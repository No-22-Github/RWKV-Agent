# DISTILL-CANARY-fd7e3b89 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a', "fixture changed"
page = " ".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"])
for turn in case["turns"]:
    for item in turn["expect"].get("output_contains", []):
        assert item in page or item in ["Plover Ledger 单个文件最多能导出多少行？", "And what about importing?"], item
print(json.dumps({"expected_contains_any": ["50000", "50,000", "5 万", "5万", "10000", "10,000", "1 万", "1万"]}, ensure_ascii=False))
