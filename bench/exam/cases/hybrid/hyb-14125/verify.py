# EXAM-CANARY-39f9b6ce : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
text = case["files"]["README.md"]
text = text.replace("3. 运行 ./configure 生成本机配置文件\n4. 把 /opt/tally/bin 加进 PATH\n5. 执行", "3. 把 /opt/tally/bin 加进 PATH\n4. 执行")
print(json.dumps({"files": {"README.md": text}}))
