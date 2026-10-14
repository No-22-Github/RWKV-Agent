"""F: no calculator; multi-step decimal arithmetic (20129-20134)."""
from decimal import ROUND_HALF_UP, Decimal

from common import has, lines, mk, value
from c_nobash import forms
from d_nodq import FORMS

BUILDERS = []
NC = ["calculator"]
HEAD = "from decimal import Decimal, ROUND_HALF_UP\nq = lambda x: x.quantize(Decimal('0.01'), ROUND_HALF_UP)\n"


def reg(f):
    BUILDERS.append(f)
    return f


def q(x):
    return Decimal(x).quantize(Decimal("0.01"), ROUND_HALF_UP)


def fc(cid, turns, files, must, body, *, sub, tt, desc, ref_text, why, ref=None, ref_calls=1):
    mk(cid, sub=sub, task_type=tt, desc=desc, files=files, turns=turns, never=NC, must=must,
       traps_notes=["No calculator: work the arithmetic out and show the working, or do it in the shell with awk."],
       ref_text=ref_text, why=why, body=body, ref_calls=ref_calls, ref=ref)


@reg
def f1():
    s = q(Decimal("12.35") * 18 + Decimal("7.8") * 26 + Decimal("129.99") * 3)
    f = {"报价/报价单.txt": lines(["螺丝套装 单价 12.35 数量 18", "密封胶 单价 7.8 数量 26", "电动起子 单价 129.99 数量 3"])}
    body = HEAD + "s = q(Decimal('12.35') * 18 + Decimal('7.8') * 26 + Decimal('129.99') * 3)\n" + FORMS
    fc("tab-20129", [("报价/报价单.txt 里三样东西各买下表上的数量，一共多少钱？保留两位小数，只回答数字。", value([], any_forms=forms(float(s)), any_token=True))], f, ["bash"],
       body, sub="F-bash", tt="policy_calc", desc="Totals three priced lines when no calculator exists (awk available)",
       ref_text="bash: awk '{s+=$3*$5} END{printf \"%%.2f\\n\", s}' 报价/报价单.txt -> %s" % s, why="Three lines, price times quantity, summed.",
       ref=(["awk '{s+=$3*$5} END{printf \"%.2f\\n\", s}' 报价/报价单.txt"], has(str(s))))


@reg
def f2():
    s = q(Decimal("898.5") * Decimal("0.85") - 30)
    f = {"price.txt": lines(["电饭煲 898.50"])}
    body = HEAD + "s = q(Decimal('898.5') * Decimal('0.85') - 30)\n" + FORMS
    fc("tab-20130", [("price.txt 里那个电饭煲打八五折以后再减 30 元，实付多少？保留两位小数，只回答数字。", value([], any_forms=forms(float(s)), any_token=True))], f, ["bash"],
       body, sub="F-bash", tt="policy_calc", desc="Applies a discount and a flat reduction when no calculator exists (awk available)",
       ref_text="bash: awk '{printf \"%%.2f\\n\", $2*0.85-30}' price.txt -> %s" % s, why="898.50 * 0.85 - 30.",
       ref=(["awk '{printf \"%.2f\\n\", $2*0.85-30}' price.txt"], has(str(s))))


@reg
def f3():
    s = q(Decimal(50000) * Decimal("0.0345") * 3)
    body = HEAD + "s = q(Decimal(50000) * Decimal('0.0345') * 3)\n" + FORMS
    fc("tab-20131", [("本金 50000 元，年利率 3.45%，单利存 3 年，到期利息是多少？保留两位小数，只回答数字。", value([], any_forms=forms(float(s)), any_token=True))], {}, ["read_file"],
       body, sub="F-mental", tt="policy_calc", desc="Computes simple interest when no calculator exists", ref_text="50000 * 0.0345 * 3 = %s (worked by hand)" % s,
       why="Simple interest, three years.", ref_calls=0)


@reg
def f4():
    a = q(Decimal("6.85") * Decimal("120.4")); b = q(a * Decimal("1.025"))
    body = (HEAD + "def fm(s):\n    f = ['%.2f' % s]\n    f.append(f[0].rstrip('0').rstrip('.'))\n    g = '{:,}'.format(int(f[0].split('.')[0])) + '.' + f[0].split('.')[1]\n"
            "    return f + [g, g.rstrip('0').rstrip('.')]\n"
            "a = q(Decimal('6.85') * Decimal('120.4'))\nb = q(a * Decimal('1.025'))\n"
            "print(json.dumps({'expected_contains_any': list(dict.fromkeys(fm(a) + fm(b)))}))\n")
    fc("tab-20132", [("120.4 美元按 6.85 的汇率换成人民币是多少？保留两位小数，只回答数字。", value([], any_forms=forms(float(a)), any_token=True)),
                     ("如果银行再收 2.5% 的手续费（加在人民币金额上），实际要付多少？同样保留两位小数，只回答数字。", value([], any_forms=forms(float(b)), any_token=True))],
       {}, ["read_file"], body, sub="F-mental-multi", tt="policy_calc", desc="Converts a currency amount and adds a fee over two turns when no calculator exists",
       ref_text="Turn 1: 120.4 * 6.85 = %s. Turn 2: * 1.025 = %s." % (a, b), why="Two chained products; turn 2 rounds the unrounded product.", ref_calls=0)


@reg
def f5():
    s = q(Decimal(7850) * Decimal("1.06") / 12)
    body = HEAD + "s = q(Decimal(7850) * Decimal('1.06') / 12)\n" + FORMS
    fc("tab-20133", [("A 12-month loan of 7,850 carries 6% flat interest on the principal. What is the monthly payment? Two decimals, number only.", value([], any_forms=forms(float(s))))],
       {}, ["read_file"], body, sub="F-mental", tt="policy_calc", desc="Computes a flat-interest monthly payment when no calculator exists",
       ref_text="7850 * 1.06 / 12 = %s" % s, why="Flat interest: principal times 1.06 spread over 12 months.", ref_calls=0)


@reg
def f6():
    s = q(Decimal("187.40") * Decimal("1.18") / 4)
    f = {"dinner.txt": lines(["Dinner bill 187.40", "Tip 18%", "Split between 4 people"])}
    body = HEAD + "s = q(Decimal('187.40') * Decimal('1.18') / 4)\n" + FORMS
    fc("tab-20134", [("Using dinner.txt, how much does each person pay (bill plus tip, split evenly)? Two decimals, number only.", value([], any_forms=forms(float(s)), required=["read_file"]))],
       f, ["read_file", "bash"], body, sub="F-bash", tt="policy_calc", desc="Splits a bill plus tip when no calculator exists",
       ref_text="read_file dinner.txt; 187.40 * 1.18 / 4 = %s (by hand or awk)" % s, why="Bill plus 18% tip over four people.", ref_calls=1)
