"""b21a sub 1 (point edits), cases 31011-31020."""
from common import L, make, RW, RL, RB, RLW, RA

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c11():
    f = {"alerts/rules.yml": L("groups:", "- name: host", "  rules:", "  - alert: HighCPU", "    expr: cpu_usage > 80", "    for: 5m", "  - alert: HighMemory", "    expr: mem_usage > 80",
        "    for: 5m", "  - alert: DiskFull", "    expr: disk_usage > 80", "    for: 5m", "- name: app", "  rules:", "  - alert: SlowRequests", "    expr: p95_latency > 800", "    for: 5m")}
    old = "  - alert: HighMemory\n    expr: mem_usage > 80\n    for: 5m\n"
    new = "  - alert: HighMemory\n    expr: mem_usage > 90\n    for: 10m\n"
    make("cfg-31011", sub="point", task_type="edit_value", desc="Two-turn tweak of one alert rule among near-identical rules",
         files=f, turns=[("alerts/rules.yml 里内存告警（HighMemory）的阈值从 80 提到 90，其他告警别动。", ["90"], None),
                         ("再把这条内存告警的持续时间从 5m 改成 10m，同样只改这一条。两次改完后告诉我这条规则现在整体长什么样。", ["10m", "90"], None)],
         ops=[[("sub", "alerts/rules.yml", old, old.replace("> 80", "> 90"))], [("sub", "alerts/rules.yml", "    expr: mem_usage > 90\n    for: 5m\n", "    expr: mem_usage > 90\n    for: 10m\n")]],
         policy=RL, notes_ref={"traps": ["TR-DECOY: three alerts share > 80 and for: 5m; turn 2 targets the same rule again."], "steps": ["read_lines", "replace line 8", "turn 2: replace line 9", "read back"],
                    "unique": "Final HighMemory rule is expr > 90, for: 10m; others unchanged."})


@reg
def c12():
    f = {"Makefile": L("CC = gcc", "CFLAGS = -O2 -Wall", "", "build:", "\t$(CC) $(CFLAGS) -o app main.c util.c", "", "debug:", "\t$(CC) -O0 -g -Wall -o app_dbg main.c util.c", "",
        "test:", "\t$(CC) $(CFLAGS) -o app_test test.c util.c", "\t./app_test", "", "clean:", "\trm -f app app_dbg app_test")}
    make("code-31012", sub="point", task_type="fix_edge_case", desc="Adds one compiler flag to a single make target while tabs must survive",
         files=f, turns=[("Makefile 里只有 test 目标需要加上 -fsanitize=address 编译选项，build 和 debug 保持不变。注意 Makefile 的命令行前面是制表符，别弄成空格。改完告诉我 test 目标现在两行是什么。", ["-fsanitize=address", "app_test"], None)],
         ops=[[("sub", "Makefile", "\t$(CC) $(CFLAGS) -o app_test test.c util.c\n", "\t$(CC) $(CFLAGS) -fsanitize=address -o app_test test.c util.c\n")]], policy=None,
         notes_ref={"traps": ["TR-DECOY: three compile lines; recipe lines must keep the leading tab."], "steps": ["read_lines Makefile", "replace_lines 11 with tab-indented line", "read back"], "unique": "Only line 11 gains the flag."})


@reg
def c13():
    f = {"team/oncall.md": L("# 值班表", "", "| 周 | 主值班 | 备值班 |", "| --- | --- | --- |", "| 第1周 | 陈雨 | 林川 |", "| 第2周 | 林川 | 王朔 |", "| 第3周 | 王朔 | 陈雨 |",
        "| 第4周 | 陈雨 | 林川 |", "", "备注：林川第 2 周起休假一周，王朔 第 3 周有培训。")}
    make("doc-31013", sub="point", task_type="write_structured", desc="Swaps a name in one row of an on-call table where the same names recur",
         files=f, turns=[("值班表里第 4 周的备值班由林川换成王朔，只改这一行。备注不用改。改完告诉我第 4 周现在是谁主谁备。", ["陈雨", "王朔"], None)],
         ops=[[("sub", "team/oncall.md", "| 第4周 | 陈雨 | 林川 |\n", "| 第4周 | 陈雨 | 王朔 |\n")]], policy=RW,
         notes_ref={"traps": ["TR-DECOY: 林川 appears in four rows and the note."], "steps": ["read_file", "replace line 8", "read back"], "unique": "Only row 8 changes."})


@reg
def c14():
    f = {"app/limits.toml": L("[global]", "max_connections = 500", "idle_timeout = 60", "", "[tenant.free]", "max_connections = 20", "idle_timeout = 60", "", "[tenant.pro]", "max_connections = 100",
        "idle_timeout = 60", "", "[tenant.enterprise]", "max_connections = 500", "idle_timeout = 120")}
    old = "[tenant.pro]\nmax_connections = 100\nidle_timeout = 60\n"
    new = "[tenant.pro]\nmax_connections = 200\nidle_timeout = 90\n"
    make("cfg-31014", sub="point", task_type="edit_value", desc="Two values in one toml table with same-valued neighbours, two turns",
         files=f, turns=[("app/limits.toml: Pro tenants now get max_connections 200. Leave every other tenant alone.", ["200"], None),
                         ("Also set the Pro tenant's idle_timeout to 90. Then tell me what the whole [tenant.pro] table looks like now.", ["idle_timeout = 90", "max_connections = 200"], None)],
         ops=[[("sub", "app/limits.toml", "[tenant.pro]\nmax_connections = 100\n", "[tenant.pro]\nmax_connections = 200\n")], [("sub", "app/limits.toml", "max_connections = 200\nidle_timeout = 60\n", "max_connections = 200\nidle_timeout = 90\n")]],
         policy=None, notes_ref={"traps": ["TR-DECOY: idle_timeout = 60 appears three times; the Pro one is line 11."], "steps": ["read_lines", "replace line 10", "replace line 11", "read back"],
                    "unique": "Pro table becomes 200 / 90."})


@reg
def c15():
    f = {"i18n/zh.json": L("{", '  "login.title": "登录",', '  "login.submit": "提交",', '  "signup.title": "注册",', '  "signup.submit": "提交",', '  "reset.title": "重置密码",', '  "reset.submit": "提交"', "}")}
    make("cfg-31015", sub="point", task_type="edit_value", desc="Changes one of three identical translation strings in a json file",
         files=f, turns=[("i18n/zh.json 里注册页的按钮文案“提交”改成“立即注册”，登录和重置密码页的按钮不要动，JSON 格式要保持合法。改完告诉我改了哪个键。", ["signup.submit", "立即注册"], None)],
         ops=[[("sub", "i18n/zh.json", '"signup.submit": "提交"', '"signup.submit": "立即注册"')]], policy=RLW,
         notes_ref={"traps": ["TR-DECOY: 提交 appears under three keys."], "steps": ["read_lines", "replace line 5", "read back"], "unique": "Only signup.submit changes."})


@reg
def c16():
    f = {"src/pricing.js": L("const TAX_RATE = 0.06;", "", "function withTax(amount) {", "  return Math.round(amount * (1 + TAX_RATE) * 100) / 100;", "}", "",
        "const SHIPPING = {", "  standard: 8,", "  express: 18,", "  overnight: 38,", "};", "", "const FREE_SHIPPING_OVER = 199;", "", "module.exports = { withTax, SHIPPING, FREE_SHIPPING_OVER };")}
    make("code-31016", sub="point", task_type="fix_edge_case", desc="Updates one shipping fee and the free-shipping threshold in a js module",
         files=f, turns=[("src/pricing.js: express shipping goes from 18 to 22 and the free shipping threshold from 199 to 259. Standard and overnight stay the same. Tell me both lines you changed.", ["22", "259"], None)],
         ops=[[("sub", "src/pricing.js", "  express: 18,\n", "  express: 22,\n"), ("sub", "src/pricing.js", "FREE_SHIPPING_OVER = 199;", "FREE_SHIPPING_OVER = 259;")]], policy=RB,
         notes_ref={"traps": ["TR-DECOY: neighbouring numbers 8/38 and 0.06."], "steps": ["sed -i on both lines", "grep -n express|FREE src/pricing.js"], "unique": "Lines 9 and 13 change."})


@reg
def c17():
    f = {"docs/runbook.md": L("# 发布手册", "", "## 步骤 1：冻结", "", "在发布前一天 18:00 冻结主干。", "", "## 步骤 2：灰度", "", "灰度比例 5%，观察 30 分钟。", "", "## 步骤 3：全量", "",
        "灰度无异常后全量，观察 30 分钟。", "", "## 步骤 4：回滚", "", "如果错误率超过 2%，在 30 分钟内回滚。")}
    make("doc-31017", sub="point", task_type="write_structured", desc="Edits one observation window in a runbook where 30 minutes repeats three times",
         files=f, turns=[("发布手册里“步骤 2：灰度”的观察时间从 30 分钟改成 45 分钟，其他步骤里的 30 分钟都是别的含义，不要改。改完告诉我改了第几行。", ["45"], None)],
         ops=[[("sub", "docs/runbook.md", "灰度比例 5%，观察 30 分钟。", "灰度比例 5%，观察 45 分钟。")]], policy=None,
         notes_ref={"traps": ["TR-DECOY: 30 分钟 appears in three steps."], "steps": ["read_lines", "replace line 9", "read back"], "unique": "Only line 9 changes."})


@reg
def c18():
    f = {"hosts.ini": L("[web]", "web1 ansible_host=10.0.1.11 ansible_port=22", "web2 ansible_host=10.0.1.12 ansible_port=22", "", "[db]", "db1 ansible_host=10.0.2.11 ansible_port=22",
        "db2 ansible_host=10.0.2.12 ansible_port=22", "", "[cache]", "cache1 ansible_host=10.0.3.11 ansible_port=22")}
    make("fs-31018", sub="point", task_type="bulk_edit", desc="Re-addresses one host and its ssh port in an inventory file across two turns",
         files=f, turns=[("hosts.ini 里 db2 这台机器换了地址，改成 10.0.2.52，别的机器不要动。", ["10.0.2.52"], None),
                         ("它的 ssh 端口也从 22 改成 2222。改完后把 db 组下的两行都告诉我。", ["2222", "10.0.2.52", "db1"], None)],
         ops=[[("sub", "hosts.ini", "db2 ansible_host=10.0.2.12 ansible_port=22\n", "db2 ansible_host=10.0.2.52 ansible_port=22\n")], [("sub", "hosts.ini", "db2 ansible_host=10.0.2.52 ansible_port=22\n", "db2 ansible_host=10.0.2.52 ansible_port=2222\n")]],
         policy=RB, notes_ref={"traps": ["TR-DECOY: ansible_port=22 on every host; turn 2 must modify db2 only."], "steps": ["sed on db2 line", "sed port", "grep db hosts.ini"], "unique": "db2 line final: 10.0.2.52 port 2222."})


@reg
def c19():
    f = {"settings/theme.css": L(":root {", "  --primary: #2b6cb0;", "  --primary-dark: #2c5282;", "  --accent: #dd6b20;", "  --bg: #ffffff;", "}", "", ".btn-primary { background: var(--primary); }", ".btn-accent { background: var(--accent); }",
        ".link { color: #2b6cb0; }")}
    make("cfg-31019", sub="point", task_type="edit_value", desc="Changes the primary colour variable but not the same hex used directly in a rule",
         files=f, turns=[("主题文件 settings/theme.css 里主色变量 --primary 换成 #1a7f64，只改变量定义这一行，别处用到同样色值的地方暂时不要改。改完告诉我改了哪一行。", ["#1a7f64"], None)],
         ops=[[("sub", "settings/theme.css", "--primary: #2b6cb0;", "--primary: #1a7f64;")]], policy=None,
         notes_ref={"traps": ["TR-DECOY: #2b6cb0 also appears in .link, which must stay."], "steps": ["read_lines", "replace line 2", "read back"], "unique": "Only --primary line changes."})


@reg
def c20():
    f = {"notes/quota.txt": L("项目配额（单位 GB）", "dev: 200", "staging: 200", "prod: 800", "backup: 800", "", "总计: 2000", "最后审核: 周三")}
    make("doc-31020", sub="point", task_type="write_structured", desc="Updates a quota line and its dependent total in a short text file",
         files=f, turns=[("notes/quota.txt 里 staging 的配额改成 300，总计要跟着改成对的。其他行别动。改完说一下总计现在是多少。", ["300", "2100"], None)],
         ops=[[("sub", "notes/quota.txt", "staging: 200\n", "staging: 300\n"), ("sub", "notes/quota.txt", "总计: 2000\n", "总计: 2100\n")]], policy=RW,
         notes_ref={"traps": ["TR-DECOY: dev and staging both 200; the total must be recomputed to 2100."], "steps": ["read_file", "replace line 3 and 7", "read back"], "unique": "staging 300, total 2100."})
