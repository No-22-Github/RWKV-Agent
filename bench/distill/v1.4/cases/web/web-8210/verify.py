# DISTILL-CANARY-ca319494 : distillation case
import json

case = json.load(open("case.json"))
firsts = {'游戏/版本.txt': '原神 当前客户端 5.2（2026-06 更新到的）'}
for p, first in firsts.items():
    assert case["files"][p].split("\n")[0] == first, p
assert len(case["files"]) == 1
local = ('游戏/版本.txt', '5.2')
if local:
    assert local[1] in case["files"][local[0]]
words = ['无法联网', '没法联网', '不能联网', '无法上网', '没法上网', '没有联网', '无法核实', '没法核实', '不能核实', '无法确认', '没法确认', '不能确认', '没法查证', '无法查证', '没办法联网', '无法在线']
excl = ['5.3', '5.4', '5.5', '5.6', '6.0', '6.1']
turn = case["turns"][0]["expect"]
assert sorted(turn["output_contains_any"]) == sorted(words)
assert sorted(turn["output_excludes"]) == sorted(excl)
print(json.dumps({"expected_contains_any": words, "expected_excludes": excl}, ensure_ascii=False))
