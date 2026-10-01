# DISTILL-CANARY-eee0903f : distillation case
import json

case = json.load(open("case.json"))
board = [l for l in case["files"]["board/specials.txt"].split("\n") if l]
promo = [l for l in case["files"]["memos/promo-week38.txt"].split("\n") if l.startswith("Saturday:")]
out = [promo[0] if l.startswith("Saturday:") else l for l in board]
print(json.dumps({"files": {"board/specials.txt": "\n".join(out) + "\n"}}))
