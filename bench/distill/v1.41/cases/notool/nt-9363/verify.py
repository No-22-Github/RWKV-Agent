# DISTILL-CANARY-8b95cc19 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'config/server.ini': 25}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"config/server.ini": "setting_01=value_01\nsetting_02=value_02\nsetting_03=value_03\nsetting_04=value_04\nsetting_05=value_05\nsetting_06=value_06\nsetting_07=value_07\nsetting_08=value_08\nsetting_09=value_09\nsetting_10=value_10\nsetting_11=value_11\nsetting_12=value_12\nsetting_13=value_13\nsetting_14=value_14\nsetting_15=value_15\nsetting_16=value_16\nsetting_17=value_17\nsetting_18=value_18\nsetting_19=value_19\nsetting_20=value_20\nsetting_21=value_21\nsetting_22=value_22\nsetting_23=value_23\nsetting_24=value_24\nsetting_25=value_25\n"}
print(json.dumps({"expected_contains_any": ["10,20p"]}, ensure_ascii=False))
