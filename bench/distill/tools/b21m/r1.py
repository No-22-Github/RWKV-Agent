"""33421-33427: ambiguous read-only questions (nt)."""
from p0 import clarify, reg

R = ("list_files", "read_file")
RB = ("list_files", "read_file", "bash")


@reg
def c33421():
    files = {"contracts/合同-恒远.md": "# 恒远采购合同\n金额 480 万元。违约金：36万元。付款：验收后 30 日内。\n",
             "contracts/合同-星河.md": "# 星河服务合同\n金额 260 万元。违约金：52万元。付款：按季度。\n"}
    clarify("nt-33421", files=files, p1="那份合同的违约金是多少？", p2="恒远那份。", stems=["合同-恒远", "合同-星河"], must=R, ans2="36万",
            excl1=["36万", "52万"], excl2=["52万"],
            desc="Asks for the penalty of 'that contract' with two contracts in the folder and nothing to pick one", ref="list 到两份合同，追问是哪一份，不先报数；用户答恒远后读并答 36万元。")


@reg
def c33422():
    files = {"proposals/proposal-alpha.md": "# Proposal Alpha\nSubmission deadline: 2026-11-14.\nBudget: 80k.\n",
             "proposals/proposal-beta.md": "# Proposal Beta\nSubmission deadline: 2026-12-02.\nBudget: 120k.\n"}
    clarify("nt-33422", files=files, p1="What's the deadline in the proposal?", p2="The beta one.", stems=["proposal-alpha", "proposal-beta"], must=R, ans2="2026-12-02",
            excl1=["2026-11-14", "2026-12-02"], excl2=["2026-11-14"],
            desc="Asks for the deadline in 'the proposal' with two proposals present", ref="Two proposals, ask which one before giving a date; then answer 2026-12-02 for beta.")


@reg
def c33423():
    a = "".join("A%03d,%d\n" % (i, 10 + i) for i in range(1, 24))
    b = "".join("B%03d,%d\n" % (i, 5 + i) for i in range(1, 32))
    files = {"orders/orders-a.csv": "id,qty\n" + a, "orders/orders-b.csv": "id,qty\n" + b}
    clarify("nt-33423", files=files, p1="那张订单表一共有多少行数据（不算表头）？", p2="b 那张。", stems=["orders-a", "orders-b"], must=RB, ans2="31",
            desc="Asks the row count of 'that order table' with two order CSVs", ref="两张订单表，追问是 a 还是 b；用户答 b 后数行（31）。")


@reg
def c33424():
    files = {"services/payments.yaml": "name: payments\nowner: Dana Whitfield\noncall: pager-2\n", "services/search.yaml": "name: search\nowner: Omar Reyes\noncall: pager-5\n"}
    clarify("nt-33424", files=files, p1="Who owns the service?", p2="Search.", stems=["payments", "search"], must=R, ans2="Omar Reyes",
            excl1=["Dana Whitfield", "Omar Reyes"], excl2=["Dana Whitfield"],
            desc="Asks who owns 'the service' with payments and search service files", ref="Two services, ask which; then answer Omar Reyes.")


@reg
def c33425():
    files = {"app-client/VERSION": "2.4.1\n", "app-server/VERSION": "3.0.2\n", "NOTES.md": "client 与 server 独立发版。\n"}
    clarify("nt-33425", files=files, p1="现在的版本号是多少？", p2="服务端的。", stems=["app-client", "app-server"], must=R, ans2="3.0.2",
            excl1=["3.0.2", "2.4.1"], excl2=["2.4.1"],
            desc="Asks for 'the current version' when client and server carry independent version files", ref="client 与 server 各有版本，追问指哪个；答服务端后读出 3.0.2。")


@reg
def c33426():
    api = "".join("2026-09-1%d 10:0%d INFO ok\n" % (i % 6, i % 9) for i in range(12)) + "".join("2026-09-15 11:%02d ERROR timeout\n" % (i * 3) for i in range(7))
    wk = "".join("2026-09-1%d 09:0%d INFO ok\n" % (i % 6, i % 9) for i in range(10)) + "".join("2026-09-14 12:%02d ERROR job failed\n" % i for i in range(14))
    files = {"logs/api.log": api, "logs/worker.log": wk}
    clarify("nt-33426", files=files, p1="日志里报了多少个 ERROR？", p2="worker 的。", stems=["api.log", "worker.log"], must=RB, ans2="14",
            desc="Asks the ERROR count 'in the log' with api.log and worker.log (7 vs 14 errors)", ref="两份日志，追问哪一份；用户答 worker 后 grep -c ERROR 得 14。")


@reg
def c33427():
    files = {"docker/web.yml": "service: web\nports:\n  - \"9443:443\"\n", "docker/admin.yml": "service: admin\nports:\n  - \"7081:80\"\n"}
    clarify("nt-33427", files=files, p1="What port does it listen on?", p2="The admin service.", stems=["web.yml", "admin.yml"], must=R, ans2="7081",
            excl1=["9443", "7081"], excl2=["9443"],
            desc="Asks which port 'it' listens on with web and admin compose files", ref="Two compose files, ask which service; admin maps host port 7081.")
