# DISTILL-CANARY-b0b2b7b0 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'素材/图片/.DS_Store': 1, '素材/图片/2026/.DS_Store': 1, '素材/音频/.DS_Store': 1, '素材/视频/.DS_Store': 1, '素材/图片/封面.png': 1, '素材/图片/2026/春季.png': 1, '素材/音频/开场.wav': 1, '素材/视频/预告.mp4': 1, '素材/模板包/.DS_Store': 1, '素材/模板包/模板.psd': 1, '素材/图片/说明.DS_Store.txt': 1, '素材/README.md': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
F = case["files"]
LINES = {'素材/图片/.DS_Store': 1, '素材/图片/2026/.DS_Store': 1, '素材/音频/.DS_Store': 1, '素材/视频/.DS_Store': 1, '素材/图片/封面.png': 1, '素材/图片/2026/春季.png': 1, '素材/音频/开场.wav': 1, '素材/视频/预告.mp4': 1, '素材/模板包/.DS_Store': 1, '素材/模板包/模板.psd': 1, '素材/图片/说明.DS_Store.txt': 1, '素材/README.md': 5}
assert sorted(F) == sorted(LINES)
for path, n in LINES.items():
    assert len(F[path].splitlines()) == n, path
assert F['素材/README.md'].startswith('# 素材库')
def plan(files):
    return {p: t for p, t in files.items() if not (p.endswith("/.DS_Store") and not p.startswith("素材/模板包/"))}
final = plan(F)
changed = {p: t for p, t in final.items() if F.get(p) != t}
removed = [p for p in F if p not in final]
assert len(changed) + len(removed) == 4
print(json.dumps({"files": changed}))
