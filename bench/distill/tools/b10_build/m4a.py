"""M4 (v1.4 §3.4) pilot, part A: the three-tool catalog (list_files, read_file, search_text)."""
from common import write_case

THREE = ["list_files", "read_file", "search_text"]
NOCALL = {"tools": [], "require_active_no_call": True}

# ---------------------------------------------------------------- code-8001
rounding = '''from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")


def round_invoice_total(amount: Decimal) -> Decimal:
    """Round an invoice total to the cent, half up, as finance requires."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def round_display(amount: Decimal) -> str:
    return f"{amount:.2f}"
'''
invoice = '''from decimal import Decimal

from billing.money import round_invoice_total


def invoice_total(lines):
    subtotal = sum((Decimal(l["qty"]) * Decimal(l["unit_price"]) for l in lines), Decimal("0"))
    return round_invoice_total(subtotal)
'''
write_case(
    "code-8001",
    desc="With only list, read and search tools offered, find which function rounds invoice totals and where it is defined",
    task_type="locate_definition", family="fam-code-b10-invoiceround-01", level="L0", ref_calls=2,
    offered_tools=THREE, axes=[],
    files={
        "billing/money.py": rounding,
        "billing/invoice.py": invoice,
        "billing/__init__.py": "",
        "reports/export.py": "def export_rows(rows):\n    return [\",\".join(str(v) for v in r) for r in rows]\n",
        "README.md": "Billing service. Money helpers live in the billing package.\n",
    },
    turns=[{
        "prompt": "Which function rounds invoice totals in this codebase, and which file defines it?",
        "expect": {"output_contains": ["round_invoice_total", "billing/money.py"], "max_output_chars": 400},
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("Billing service.")
defs = [(p, m) for p, t in files.items() if p.endswith(".py") for m in re.findall(r"^def (\\w+)\\(", t, re.M) if "invoice" in m and "round" in m]
assert len(defs) == 1
print(json.dumps({"expected_string": defs[0][0]}))
''',
    notes='''
## Traps
- None. The case teaches using only the three offered tools.

## Reference solution
1. Search the workspace for "round" (or list billing/ and read billing/invoice.py).
2. billing/money.py defines round_invoice_total (quantize to the cent, ROUND_HALF_UP); billing/invoice.py imports and calls it.
Final answer in one sentence: round_invoice_total in billing/money.py rounds totals to the cent, half up; invoice_total in billing/invoice.py calls it. Criteria: contains round_invoice_total and billing/money.py.

## Why the answer is unique
Only one function definition has both "round" and "invoice" in its name; round_display formats for display and does not round totals.
''',
)

# ---------------------------------------------------------------- doc-8003
handbook = "# 员工手册（2026 版）\n\n" + "".join(
    "## 第 %d 章 %s\n\n%s\n\n" % (i + 1, t, b) for i, (t, b) in enumerate([
        ("总则", "本手册适用于栖霞科技全体正式员工。"),
        ("考勤", "标准工时为每日 8 小时，弹性上班时间 8:30–10:00。"),
        ("请假", "病假需提供医院证明；事假每年累计不超过 10 天。"),
        ("年假", "工作满 1 年不满 10 年的，年假 10 天；满 10 年的，年假 15 天。当年未休完的年假可结转至次年 3 月 31 日前使用，结转上限 5 天，逾期作废。"),
        ("报销", "差旅报销须在出差结束后 30 天内提交。"),
        ("设备", "笔记本电脑使用年限为 4 年。"),
    ]))
write_case(
    "doc-8003",
    desc="With only list, read and search tools offered, look up how many unused annual-leave days can carry over in the employee handbook",
    task_type="policy_lookup", family="fam-doc-b10-leavecarry-01", level="L0", ref_calls=2,
    offered_tools=THREE, axes=[],
    files={
        "制度/员工手册.md": handbook,
        "制度/考勤补充说明.md": "2026 年 5 月起，远程办公日也需在系统打卡。\n",
        "README.md": "人事制度文档。\n",
    },
    turns=[{
        "prompt": "我今年还有 7 天年假没休，最多能带到明年几天？",
        "expect": {"output_contains": ["5"], "output_contains_token": True, "output_contains_any": ["3 月 31", "3月31"], "max_output_chars": 400},
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
text = case["files"]["制度/员工手册.md"]
assert text.startswith("# 员工手册")
cap = int(re.search(r"结转上限 (\\d+) 天", text).group(1))
print(json.dumps({"expected_number": cap}))
''',
    notes='''
## Traps
- None. 只提供三个工具，正常检索即可。

## Reference solution
1. 搜索「结转」或读 制度/员工手册.md 第 4 章：当年未休完的年假可结转至次年 3 月 31 日前使用，结转上限 5 天，逾期作废。
终答 1–2 句：7 天里最多带 5 天到明年，而且要在明年 3 月 31 日前休完，剩下 2 天作废。判据：包含 5（独立词元）和 3 月 31 日。

## Why the answer is unique
手册只有一处结转规定，上限 5 天，7 天超过上限，所以是 5 天。
''',
)

# ---------------------------------------------------------------- fs-8003
mig = {"db/migrations/%s" % n: "-- migration\n" for n in [
    "0001_create_accounts.sql", "0002_create_invoices.sql", "0003_add_invoice_status.sql",
    "0004_create_payments.sql", "0005_index_payments_account.sql", "0006_add_currency.sql",
    "0007_backfill_currency.sql"]}
mig.update({"db/migrations/README.md": "Apply in numeric order.\n", "db/migrations/.keep": "",
            "db/seeds/demo.sql": "-- demo rows\n", "README.md": "Payments service.\n"})
write_case(
    "fs-8003",
    desc="With only list, read and search tools offered, count the SQL migration files in the migrations directory, excluding seeds and docs",
    task_type="count_by_type", family="fam-fs-b10-migrationcount-01", level="L0", ref_calls=1,
    offered_tools=THREE, axes=[],
    files=mig,
    turns=[{
        "prompt": "How many SQL migration files are in db/migrations right now?",
        "expect": {"output_contains": ["7"], "output_contains_token": True, "max_output_chars": 300},
    }],
    verify='''
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Payments service.")
assert case["files"]["db/migrations/README.md"].startswith("Apply in numeric order")
n = sum(1 for p in case["files"] if p.startswith("db/migrations/") and p.endswith(".sql"))
print(json.dumps({"expected_number": n}))
''',
    notes='''
## Traps
- None.

## Reference solution
1. List db/migrations: seven .sql files (0001 to 0007), plus README.md and .keep.
Final answer in one sentence: there are 7 migration files, 0001_create_accounts.sql through 0007_backfill_currency.sql. Criteria: contains 7 as a whole token.

## Why the answer is unique
db/seeds/demo.sql is outside the migrations directory; README.md and .keep are not SQL files.
''',
)

# ---------------------------------------------------------------- nt-8004
write_case(
    "nt-8004",
    desc="Only list, read and search tools are offered and the question is plain arithmetic, so it must be answered directly without a calculator",
    task_type="unit_convert", family="fam-nt-b10-oilrefill-01", level="L0", ref_calls=0,
    offered_tools=THREE, axes=["DEC"],
    files={},
    turns=[{
        "prompt": "一桶润滑油 18.9 升，保养时每台机器加 0.75 升，这一桶最多够加几台？",
        "expect": dict(NOCALL, output_contains=["25"], output_contains_token=True, max_output_chars=300),
    }],
    verify='''
import json

case = json.load(open("case.json"))
assert "18.9 升" in case["turns"][0]["prompt"]
print(json.dumps({"expected_number": int(18.9 / 0.75)}))
''',
    notes='''
## Traps
- None. 清单里没有计算器，这是一步除法，直接算。

## Reference solution
不调用工具：18.9 ÷ 0.75 = 25.2，按整台算最多 25 台，剩 0.15 升。终答 1–2 句写出算式。判据：零调用、包含 25。

## Why the answer is unique
25.2 台取整为 25 台；第 26 台需要 19.5 升，超过一桶。
''',
)

# ---------------------------------------------------------------- nt-8005
write_case(
    "nt-8005",
    desc="Only list, read and search tools are offered and the user asks for a translation, which needs no tool",
    task_type="concept", family="fam-nt-b10-noticetranslate-01", level="L0", ref_calls=0,
    offered_tools=THREE, axes=["DEC"],
    files={},
    turns=[{
        "prompt": "Please translate this notice into English for our overseas customers: 本周五 18:00 至 22:00 进行数据库维护，期间订单查询服务暂停。",
        "expect": dict(NOCALL, output_contains=["Friday", "18:00", "22:00"], output_contains_any=["maintenance"], max_output_chars=400),
    }],
    verify='''
import json

case = json.load(open("case.json"))
src = case["turns"][0]["prompt"].split(": ", 1)[1]
assert "18:00" in src and "22:00" in src and "周五" in src
print(json.dumps({"expected_contains_any": ["maintenance"]}))
''',
    notes='''
## Traps
- None. Translation needs no tool.

## Reference solution
No tool call. Reply with the translation, e.g. "Database maintenance will take place this Friday from 18:00 to 22:00; the order lookup service will be unavailable during that time." Criteria: zero calls; contains Friday, 18:00, 22:00 and maintenance.

## Why the answer is unique
A direct translation; the times are kept in the source's 24-hour form.
''',
)
