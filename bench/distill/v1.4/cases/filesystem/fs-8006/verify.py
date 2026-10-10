# DISTILL-CANARY-8f94b25d : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
# sabotage guard: bank verify deletes the first non-empty line of this file first
assert files["README.md"].splitlines()[0] == "# 拾光映画 交付目录"

reg = files["交付/上传登记.md"]
assert reg.splitlines()[0] == "# 交付包上传登记"
rows = [l for l in reg.splitlines() if l.startswith("| 林晚棠 | 海景婚纱-精修包")]
assert len(rows) == 1 and "返修" in rows[0]
assert not any(p.startswith("交付/林晚棠") and "精修包" in p for p in files)
# Decoys: the same client's selection pack and another client's pack exist.
assert "交付/林晚棠-海景婚纱-初选包.zip" in files
assert "交付/周叙-城市旅拍-精修包.zip" in files
words = ["返修", "修图", "修改", "重传", "重新上传", "未上传", "没有上传", "还没上传", "尚未上传", "暂无", "未交付", "还没交付", "尚未交付"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
