# DISTILL-CANARY-d0b0b6a8 : distillation case
import json

case = json.load(open("case.json"))
firsts = {'出差/行程.md': '9 月 22 日 北京-广州，下午航班，带一个登机箱。'}
for p, first in firsts.items():
    assert case["files"][p].split("\n")[0] == first, p
assert len(case["files"]) == 1
local = None
if local:
    assert local[1] in case["files"][local[0]]
words = ['无法联网', '没法联网', '不能联网', '无法上网', '没法上网', '没有联网', '无法核实', '没法核实', '不能核实', '无法确认', '没法确认', '不能确认', '没法查证', '无法查证', '没办法联网', '无法在线']
excl = ['免费托运 20', '免费托运20', '免费托运 30', '免费托运30', '免费托运 40', '免费托运40']
turn = case["turns"][0]["expect"]
assert sorted(turn["output_contains_any"]) == sorted(words)
assert sorted(turn["output_excludes"]) == sorted(excl)
print(json.dumps({"expected_contains_any": words, "expected_excludes": excl}, ensure_ascii=False))
