# DISTILL-CANARY-13dbd176 : distillation case
import json

case = json.load(open("case.json"))
firsts = {'合同/兼职协议.txt': '兼职协议摘要'}
for p, first in firsts.items():
    assert case["files"][p].split("\n")[0] == first, p
assert len(case["files"]) == 1
local = ('合同/兼职协议.txt', '2420 元')
if local:
    assert local[1] in case["files"][local[0]]
words = ['无法联网', '没法联网', '不能联网', '无法上网', '没法上网', '没有联网', '无法核实', '没法核实', '不能核实', '无法确认', '没法确认', '不能确认', '没法查证', '无法查证', '没办法联网', '无法在线']
excl = ['2540 元', '2540元', '2600 元', '2600元', '2500 元', '2500元', '2480 元', '2480元']
turn = case["turns"][0]["expect"]
assert sorted(turn["output_contains_any"]) == sorted(words)
assert sorted(turn["output_excludes"]) == sorted(excl)
print(json.dumps({"expected_contains_any": words, "expected_excludes": excl}, ensure_ascii=False))
