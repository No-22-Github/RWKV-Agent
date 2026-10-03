"""M8 (v1.4 §3.8) pilot, part A: the calculator is offered and the answer needs real arithmetic."""
from common import write_case

CALC = ["calculator"]

def strip(v):
    return v.rstrip("0").rstrip(".") if "." in v else v

def forms(x, nd=2):
    a = "%.*f" % (nd, x)
    b = "{:,.{}f}".format(x, nd)
    return sorted({a, b})

# ---------------------------------------------------------------- nt-8006
tr = round(350 / 3.517, 2)
write_case(
    "nt-8006",
    desc="Convert a chiller's cooling capacity from kW to refrigeration tons with a non-integer factor, rounded to two decimals",
    task_type="unit_convert", family="fam-nt-b10-chillertons-01", level="L0", ref_calls=1, axes=[], files={},
    turns=[{"prompt": "一台冷水机组的制冷量是 350 kW，换算成冷吨是多少？按 1 冷吨 = 3.517 kW 算，保留两位小数。",
            "expect": {"output_contains": ["%.2f" % tr], "required_tools": CALC, "max_output_chars": 300}}],
    verify='''
import json

case = json.load(open("case.json"))
assert "350 kW" in case["turns"][0]["prompt"] and "3.517 kW" in case["turns"][0]["prompt"]
print(json.dumps({"expected_number": round(350 / 3.517, 2)}))
''',
    notes='''
## Traps
- None. 清单里有计算器，除数是非整数，按 §3.8 必须交给计算器。

## Reference solution
1. calculator：350 / 3.517，precision 2 → %.2f。
终答一句话：约 %.2f 冷吨（350 ÷ 3.517）。判据：包含 %.2f，调用过 calculator。

## Why the answer is unique
换算系数和保留位数都由题面给定。
''' % (tr, tr, tr),
)

# ---------------------------------------------------------------- nt-8007
a = 18240 * 5 // 100
b = 19100 * 4 // 100
write_case(
    "nt-8007",
    desc="Two-step percentage arithmetic on subscriber churn across two months, answer as a bare number",
    task_type="unit_convert", family="fam-nt-b10-churndelta-01", level="L0", ref_calls=2, axes=[], files={},
    turns=[{"prompt": "In August 5% of our 18,240 subscribers churned; in September 4% of 19,100 churned. How many fewer subscribers churned in September than in August? Give the number only.",
            "expect": {"expected_number": a - b, "tolerance": 0.01, "required_tools": CALC}}],
    verify='''
import json

case = json.load(open("case.json"))
p = case["turns"][0]["prompt"]
assert "18,240" in p and "19,100" in p
print(json.dumps({"expected_number": 18240 * 0.05 - 19100 * 0.04}))
''',
    notes='''
## Traps
- None. The user asks for the number only, so the reply is the bare value.

## Reference solution
1. calculator: 18240 * 0.05 - 19100 * 0.04 = %d (912 - 764).
Final answer: %d. Criteria: expected_number %d, calculator used.

## Why the answer is unique
Both percentages yield whole subscribers; the difference is fixed.
''' % (a - b, a - b, a - b),
)

# ---------------------------------------------------------------- nt-8008
days = 14 + 31 + 30 + 31
fee = round(12800 * days / 365, 2)
write_case(
    "nt-8008",
    desc="Prorate an annual fee over a date range that spans four months, inclusive of both ends, on a 365-day basis",
    task_type="unit_convert", family="fam-nt-b10-prorate-01", level="L0", ref_calls=2, axes=[], files={},
    turns=[{"prompt": "一项软件服务年费 12800 元，我们从 9 月 17 日用到 12 月 31 日（首尾都算），按一年 365 天折算，应付多少元？保留两位小数。",
            "expect": {"output_contains_any": forms(fee), "required_tools": CALC, "max_output_chars": 300}}],
    verify='''
import json
from datetime import date

case = json.load(open("case.json"))
assert "12800 元" in case["turns"][0]["prompt"]
d = (date(2026, 12, 31) - date(2026, 9, 17)).days + 1
fee = round(12800 * d / 365, 2)
print(json.dumps({"expected_contains_any": sorted({"%.2f" % fee, "{:,.2f}".format(fee)})}))
''',
    notes='''
## Traps
- None. 天数要含首尾：9 月 17–30 日 14 天 + 10 月 31 + 11 月 30 + 12 月 31 = %d 天。

## Reference solution
1. 数天数（可心算或用 calculator 加 14+31+30+31）：%d 天。
2. calculator：12800 * %d / 365，precision 2 → %.2f。
终答一句话：按 %d 天折算应付 %.2f 元（12800 × %d ÷ 365）。判据：包含金额（带或不带千分位），调用过 calculator。

## Why the answer is unique
日期区间、首尾计入与 365 天口径都在题面给定。
''' % (days, days, days, fee, days, fee, days),
)

# ---------------------------------------------------------------- nt-8009
total = 37.5 * 86.40 + 7.5 * 86.40 * 1.5
write_case(
    "nt-8009",
    desc="Contractor invoice with regular and time-and-a-half overtime hours at a decimal hourly rate, answered as a plain number",
    task_type="unit_convert", family="fam-nt-b10-overtimeinvoice-01", level="L0", ref_calls=1, axes=[], files={},
    turns=[{"prompt": "A contractor logged 37.5 regular hours at $86.40 an hour and 7.5 overtime hours at 1.5 times that rate. What is the invoice total in dollars? Give it as a plain number.",
            "expect": {"expected_number": total, "tolerance": 0.01, "required_tools": CALC}}],
    verify='''
import json

case = json.load(open("case.json"))
assert "$86.40" in case["turns"][0]["prompt"]
print(json.dumps({"expected_number": 37.5 * 86.40 + 7.5 * 86.40 * 1.5}))
''',
    notes='''
## Traps
- None.

## Reference solution
1. calculator: 37.5 * 86.40 + 7.5 * 86.40 * 1.5 = %g (3240 + 972).
Final answer: %g. Criteria: expected_number, calculator used.

## Why the answer is unique
Rate, hours and multiplier are all given.
''' % (total, total),
)

# ---------------------------------------------------------------- nt-8010
pct = round((3217 - 2846) / 2846 * 100, 1)
write_case(
    "nt-8010",
    desc="Year-over-year revenue growth percentage to one decimal, answered as a bare number",
    task_type="unit_convert", family="fam-nt-b10-yoygrowth-01", level="L0", ref_calls=1, axes=[], files={},
    turns=[{"prompt": "去年营收 2846 万元，今年 3217 万元，同比增长百分之几？保留一位小数，只回数字，不带百分号。",
            "expect": {"expected_number": pct, "tolerance": 0.05, "required_tools": CALC}}],
    verify='''
import json

case = json.load(open("case.json"))
assert "2846 万元" in case["turns"][0]["prompt"]
print(json.dumps({"expected_number": round((3217 - 2846) / 2846 * 100, 1)}))
''',
    notes='''
## Traps
- None. 用户要求只回数字。

## Reference solution
1. calculator：(3217 - 2846) / 2846 * 100，precision 1 → %.1f。
终答：%.1f。判据：expected_number %.1f，调用过 calculator。

## Why the answer is unique
同比增长率 = 增量 ÷ 去年值，题面给定保留一位。
''' % (pct, pct, pct),
)
