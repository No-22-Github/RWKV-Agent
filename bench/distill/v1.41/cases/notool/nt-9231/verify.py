# DISTILL-CANARY-be9d27b4 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'素材/封面.psd': 1, '素材/视频/开场.mov': 1, '素材/音频/配乐.wav': 1}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"素材/封面.psd": "placeholder 1\n", "素材/视频/开场.mov": "placeholder 2\n", "素材/音频/配乐.wav": "placeholder 3\n"}
print(json.dumps({"expected_contains_any": ["-size +10M", "-size +10240k", "-size +10485760c", "-size +10"]}, ensure_ascii=False))
