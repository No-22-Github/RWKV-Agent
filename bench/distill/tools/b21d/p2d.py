"""31363-31370: controls, a single candidate exists so the model should just do it."""
from p2 import solo, reg
from p2b import mklog, COUNT
from p2c import RX, CSV_SUM

W = ("list_files", "read_file", "write_file")
R = ("list_files", "read_file", "search_text")


@reg
def c31363():
    files = {"config/app.yaml": "name: shop\ntimeout: 30\nretries: 3\n", "README.md": "# shop\n"}
    solo("cfg-31363", task_type="edit_value", files=files, p1="把超时时间改成 45 秒。", must=W, rules={"config/app.yaml": ("sub", "timeout: 30", "timeout: 45")},
         desc="Asks to set the timeout to 45 when only one config file exists", ref="只有 app.yaml 一个配置，直接把 timeout 改 45。")


@reg
def c31364():
    files = {"clients/main.yaml": "name: main\nretry: 3\nbackoff: 2\n", "docs/notes.md": "client notes\n"}
    solo("cfg-31364", task_type="edit_value", files=files, p1="Raise the retry count to 5.", must=W, rules={"clients/main.yaml": ("sub", "retry: 3", "retry: 5")},
         desc="Asks to raise the retry count to 5 when only one client config exists", ref="唯一的 client 配置，直接改 retry: 5。")


@reg
def c31365():
    files = {"logs/app.log": mklog("2026-09-16", 14, 14)}
    solo("log-31365", task_type="count_events", files=files, p1="统计一下报错有多少条。", must=R, calc=COUNT % ("logs/app.log", "ERROR"), ans="14",
         desc="Asks for the error count when exactly one log exists", ref="只有 app.log 一份，直接数 ERROR 行 = 14。")


@reg
def c31366():
    files = {"logs/deploy.log": "2026-09-13 10:00 deploy v1.4.0 finished\n2026-09-15 17:45 deploy v1.4.1 finished\n", "README.md": "# ops\n"}
    solo("log-31366", task_type="time_window", files=files, p1="When did the last deploy happen?", must=R,
         calc='ans = [l for l in case["files"]["logs/deploy.log"].splitlines()][-1].split()[0]', ans="2026-09-15",
         desc="Asks for the last deploy time when exactly one deploy log exists", ref="唯一的 deploy.log，最后一行 2026-09-15 17:45。")


@reg
def c31367():
    files = {"minutes/0912-财务.md": "# 财务例会 9/12\n决定：Q4 预算总额 380 万。\n", "minutes/template.md": "# 会议纪要模板\n决定：\n"}
    solo("nt-31367", task_type="ambiguous_request", files=files, p1="把那份会议纪要总结一下，预算是多少？", must=R, calc=RX % (r"总额 (\d+) 万", "minutes/0912-财务.md"), ans="380",
         traps=["TR-DECOY"], desc="Asks to summarise the meeting note when one real note and a blank template exist", ref="模板不是纪要，只有财务那份有内容，直接总结，预算 380 万。")


@reg
def c31368():
    files = {"finance/expenses-q3.csv": "item,cost\nlaptops,2100\ntravel,3300\ntraining,1250\n", "finance/expenses-q3.csv.bak": "item,cost\nlaptops,0\n"}
    solo("tab-31368", task_type="aggregate", files=files, p1="Total the expenses.", must=R, calc=CSV_SUM % ("cost", "finance/expenses-q3.csv"), ans="6650",
         traps=["TR-DECOY"], desc="Asks to total expenses with one real file and a stale .bak copy", ref="只有 expenses-q3.csv 是有效文件，合计 6650。")


@reg
def c31369():
    files = {"config/prod.yaml": "name: shop\nport: 8080\n", "config/prod.yaml.bak": "name: shop\nport: 8000\n"}
    solo("cfg-31369", task_type="edit_value", files=files, p1="把端口改成 9000。", must=W, p2="现在配置里的端口是多少？", out2=["9000"],
         rules={"config/prod.yaml": ("sub", "port: 8080", "port: 9000")}, traps=["TR-DECOY"],
         desc="Asks to change the port when one live config and its .bak exist", ref="只有 prod.yaml 是当前配置，.bak 不动；改 9000 后读回确认。")


@reg
def c31370():
    files = {"stats/sales.csv": "day,units\n1,40\n2,55\n3,45\n", "stats/notes.txt": "单位：件\n"}
    solo("tab-31370", task_type="aggregate", files=files, p1="算一下总销量。", must=R, calc=CSV_SUM % ("units", "stats/sales.csv"), ans="140", p2="平均每天呢？", out2=["46"],
         traps=["TR-DECOY"], desc="Asks for total units sold when one data file exists; follow-up asks for the daily average", ref="sales.csv 合计 140，平均 46.67。")
