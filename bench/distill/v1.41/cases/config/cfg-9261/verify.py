# DISTILL-CANARY-740993dc : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 28
assert case["files"]['数据源/README.md'].startswith('# 数据源')
assert 'pool.size.min 是最小空闲连接数' in case["files"]['数据源/README.md']
FINAL = json.loads(r'''{"数据源/用户.properties": "# 用户库\nurl=jdbc:mysql://db-用户:3306/用户\npool.size=20\npool.size.min=10\n", "数据源/报表.properties": "# 报表库\nurl=jdbc:mysql://db-报表:3306/报表\npool.size=40\npool.size.min=10\n", "数据源/日志.properties": "# 日志库\nurl=jdbc:mysql://db-日志:3306/日志\npool.size=20\npool.size.min=10\n", "数据源/风控.properties": "# 风控库\nurl=jdbc:mysql://db-风控:3306/风控\npool.size=20\npool.size.min=10\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"数据源/订单.properties": 1, "数据源/_归档/旧库.properties": 1, "数据源/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
