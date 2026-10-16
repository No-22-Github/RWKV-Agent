"""31397-31409: code, table and mixed lookups phrased like general questions."""
from p3 import local, reg, fx


@reg
def c31397():
    files = {"src/retry.py": "MAX_RETRIES = 12\nBACKOFF_SECONDS = 1.5\n\n\ndef run(fn):\n    for _ in range(MAX_RETRIES):\n        fn()\n", "src/other.py": "MAX_RETRIES = 3\n"}
    local("code-31397", tt="locate_definition", files=files, q="我们的重试最多几次？", path="src/retry.py", pat=r"MAX_RETRIES = (\d+)\nBACKOFF", variant="A", decoy="3",
          desc="Asks the max retry count; retry.py has the constant, a decoy module has another", ref="读 src/retry.py：12 次。")


@reg
def c31398():
    files = {"app/auth.py": "TOKEN_TTL_HOURS = 36\n\n\ndef issue(user):\n    return sign(user, hours=TOKEN_TTL_HOURS)\n", "app/session.py": "SESSION_TTL_HOURS = 8\n"}
    local("code-31398", tt="locate_definition", files=files, q="How long is a login token valid, in hours?", path="app/auth.py", pat=r"TOKEN_TTL_HOURS = (\d+)", variant="B", decoy="8",
          desc="Asks the token validity in hours; auth.py holds it, session.py a similar constant", ref="读 app/auth.py：36 小时。")


@reg
def c31399():
    files = {"server/routes.py": "ROUTES = {\n    '/health': 'health',\n    '/v2/orders': 'orders_v2',\n    '/v2/refunds': 'refunds',\n}\n", "server/legacy.py": "ROUTES = {'/orders': 'orders_v1'}\n"}
    local("code-31399", tt="locate_definition", files=files, q="退款接口的路径是什么？", path="server/routes.py", pat=r"'(/v2/refunds)'", variant="A", decoy="/orders",
          desc="Asks the refund endpoint path; the routes table has it", ref="读 server/routes.py：/v2/refunds。")


@reg
def c31400():
    files = {"lib/pricing.py": "VIP_DISCOUNT = 0.85\nSTUDENT_DISCOUNT = 0.9\n", "lib/tests.py": "assert VIP_DISCOUNT == 0.85\n"}
    local("code-31400", tt="locate_definition", files=files, q="VIP 客户打几折？", path="lib/pricing.py", pat=r"VIP_DISCOUNT = (0\.\d+)", variant="B", decoy="0.9",
          desc="Asks the VIP discount; pricing.py has the multiplier 0.85", ref="读 lib/pricing.py：0.85（八五折）。")


@reg
def c31401():
    files = {"tools/cli.py": "import argparse\np = argparse.ArgumentParser()\np.add_argument('--batch-size', type=int, default=256)\np.add_argument('--workers', type=int, default=4)\n", "tools/README.md": "# tools\n"}
    local("code-31401", tt="locate_definition", files=files, q="What's the default batch size of our CLI?", path="tools/cli.py", pat=r"batch-size', type=int, default=(\d+)", variant="A", decoy="4",
          desc="Asks the CLI default batch size; defined in cli.py", ref="读 tools/cli.py：256。")


@reg
def c31402():
    files = {"core/errors.py": "ERROR_CODES = {\n    'E101': 'invalid input',\n    'E207': 'quota exceeded',\n    'E315': 'upstream unavailable',\n}\n", "docs/errors.md": "# Errors\nSee core/errors.py\n"}
    local("code-31402", tt="locate_definition", files=files, q="错误码 E207 是什么意思？", path="core/errors.py", pat=r"'E207': '([a-z ]+)'", variant="B", decoy="invalid input",
          desc="Asks the meaning of an error code written as if it were a public code; the project table defines it", ref="读 core/errors.py：quota exceeded。")


@reg
def c31403():
    files = {"data/staff.csv": "name,dept,level\nAnn,eng,L5\nBo,ops,L3\nCy,eng,L4\n", "data/readme.txt": "staff export\n"}
    local("tab-31403", tt="aggregate", files=files, q="Ann 是什么职级？", path="data/staff.csv", pat=r"Ann,eng,(L\d)", variant="A", decoy="L4",
          desc="Asks Ann's level as if she were a public figure; the staff table has it", ref="读 data/staff.csv：L5。")


@reg
def c31404():
    files = {"data/prices.csv": "sku,name,price\nK100,键盘,299\nM200,鼠标,129\nS300,显示器,1899\n", "data/prices-old.csv": "sku,name,price\nS300,显示器,2099\n"}
    local("tab-31404", tt="aggregate", files=files, q="显示器现在卖多少钱？", path="data/prices.csv", pat=r"S300,显示器,(\d+)", variant="B", decoy="2099",
          desc="Asks the monitor's price now; the current price file and an old one differ", ref="读 data/prices.csv：1899。")


@reg
def c31405():
    files = {"sales/targets.csv": "region,q3_target\nnorth,1200\nsouth,950\neast,1430\n", "sales/actuals.csv": "region,q3_actual\nnorth,1010\nsouth,990\neast,1500\n"}
    local("tab-31405", tt="aggregate", files=files, q="What's the Q3 target for the east region?", path="sales/targets.csv", pat=r"east,(\d+)", variant="A", decoy="1500",
          desc="Asks the east region's Q3 target; the actuals file holds a near-miss figure", ref="读 sales/targets.csv：1430（actuals 的 1500 是实际值）。")


@reg
def c31406():
    files = {"inventory/stock.csv": "sku,qty\nA-10,340\nB-20,0\nC-30,55\n", "inventory/orders.csv": "sku,qty\nA-10,60\n"}
    local("tab-31406", tt="aggregate", files=files, q="A-10 现在还有多少库存？", path="inventory/stock.csv", pat=r"A-10,(\d+)", variant="B", decoy="60",
          desc="Asks the stock of an SKU; stock.csv has it and orders.csv has another number for the same SKU", ref="读 inventory/stock.csv：340。")


@reg
def c31407():
    files = {"faq/internal.md": "# 内部 FAQ\n\n问：报销多久到账？答：审批通过后 5 个工作日内到账。\n问：年会什么时候？答：12 月 19 日。\n", "faq/public.md": "# 对外 FAQ\n\n退款 7 个工作日到账。\n"}
    local("doc-31407", tt="policy_lookup", files=files, q="年会是几号？", path="faq/internal.md", pat=r"答：(12 月 19 日)", variant="A", decoy="12 月 25 日",
          desc="Asks the date of the annual party; only the internal FAQ knows", ref="读 faq/internal.md：12 月 19 日。")


@reg
def c31408():
    files = {"people/directory.md": "# 通讯录\n\n- 后端负责人：韩雪，分机 8204\n- 前端负责人：吴迪，分机 8317\n- 运维值班：见排班表\n", "people/org.md": "# 组织架构\n"}
    local("doc-31408", tt="policy_lookup", files=files, q="Who leads the frontend team, and what's their extension?", path="people/directory.md", pat=r"前端负责人：吴迪，分机 (8317)", variant="B", decoy="8204",
          desc="Asks who leads the frontend team and their extension; only the directory has it", ref="读 people/directory.md：吴迪，分机 8317。")


@reg
def c31409():
    files = {"wiki/wifi.md": "# 办公室网络\n\n访客 Wi-Fi：Guest-5G，密码每周一更换，见前台白板。\n员工 Wi-Fi：Corp-Secure，使用域账号登录。\n", "wiki/printers.md": "# 打印机\n三楼：HP-3F。\n"}
    local("doc-31409", tt="policy_lookup", files=files, q="办公室员工 Wi-Fi 叫什么名字？", path="wiki/wifi.md", pat=r"员工 Wi-Fi：(Corp-Secure)", variant="A", decoy="Guest-5G",
          desc="Asks the staff Wi-Fi name; only the office wiki has it while a web tip shows only generic naming", ref="读 wiki/wifi.md：Corp-Secure。")
