# DISTILL-CANARY-5a4dd4de : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
cards = csv.DictReader(io.StringIO(case["files"]["hives/box_card.csv"]))
card = next(cards)
cells = (int(card["deep_boxes"]) * int(card["frames_per_box"])
         * int(card["cells_per_side"]) * 2)
print(json.dumps({"expected_number": cells}))
