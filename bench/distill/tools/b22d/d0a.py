"""D0 part a: large, multi-step, precise arithmetic where a calculator is the right move (hyb-34351..34360)."""
from common import T, W, mk


def one(i, prompts, compute, given, note, decoy, alts):
    must = ["calculator"] if i % 2 else ["calculator", "bash"]
    mk("hyb-%d" % (34350 + i), sub="D0", turns=prompts, compute=compute, given=given, decoy=decoy, notes=note,
       must=must, files=W(i), rc=1, alts=alts)


def build():
    def c1():
        r, n, p = 0.042 / 12, 300, 850000
        m = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
        return [round(m, 2), round(m * n - p, 2)]
    one(1, [T("帮我算一下，房贷 850000 元，年利率 4.2%，贷 25 年，等额本息，每个月要还多少？保留两位小数。", tol=0.006),
            T("那 25 年一共要付多少利息？", tol=2.0)], c1, ["850000", "4.2%", "25 年"],
        "Equal-instalment mortgage. r=0.042/12, n=300, M = P*r*(1+r)^n/((1+r)^n-1) = 4581.01; interest = 300M-P = 524302.91.",
        "3570", ["贷款 85 万 25 年月供", "等额本息 4.2% 25 年每月还款", "房贷月供和总利息", "85 万商贷月供两位小数", "monthly payment on 850000 over 25 years at 4.2%"])

    def c2():
        r, n, p = 0.069 / 12, 60, 32500
        return [round(p * r * (1 + r) ** n / ((1 + r) ** n - 1), 2)]
    one(2, [T("Can you work out the monthly payment on a $32,500 car loan at 6.9% APR over 60 months? Two decimals, standard amortized formula.", tol=0.006)],
        c2, ["32,500", "6.9%", "60 months"], "Amortized payment. P*r/(1-(1+r)^-n) with r=0.069/12, n=60.", "541.67",
        ["car loan payment 32500 at 6.9% for 60 months", "monthly installment, 60-month auto loan", "amortization payment on $32,500", "APR 6.9% five-year loan payment", "车贷 32500 美元 60 期月供"])

    def c3():
        return [round(150000 * 1.0385 ** 7, 2), round(150000 * 1.0385 ** 10, 2)]
    one(3, [T("帮我算一下，15 万元年利率 3.85%，每年复利一次，存 7 年本息合计多少？保留两位小数。", tol=0.006), T("如果改成存 10 年呢？", tol=0.006)],
        c3, ["15 万", "3.85%", "7 年"], "Compound deposit. 150000*1.0385^7 and ^10.", "190395",
        ["15 万元存 7 年复利 3.85%", "本息合计，7 年，再算 10 年", "年复利 3.85% 的终值", "十五万七年后多少钱", "150000 at 3.85% compounded for 7 years"])

    def c4():
        return [round(93.4 * 0.25 + 81.75 * 0.35 + 76.2 * 0.4, 2)]
    one(4, [T("帮我算一下总评成绩：平时 93.4 分占 25%，期中 81.75 分占 35%，期末 76.2 分占 40%，加权后是多少？保留两位小数。", tol=0.006)], c4,
        ["93.4", "81.75", "76.2"], "Weighted score. 23.35+28.6125+30.48 = 82.4425.", "83.78",
        ["三项成绩加权平均", "平时期中期末按 25 35 40 加权", "总评分保留两位", "加权总评 93.4 81.75 76.2", "weighted course grade from three components"])

    def c5():
        usd = 12480 * 1.0873
        jpy = usd * 149.62
        return [round(jpy * (1 - 0.0035), 2)]
    one(5, [T("I'm converting 12,480 EUR to USD at 1.0873, then that USD to JPY at 149.62, and the bank takes 0.35% of the final JPY amount. How many yen do I end up with? Two decimals.", tol=0.006)],
        c5, ["12,480", "1.0873", "149.62", "0.35%"], "Two-leg conversion minus fee.", "2030000",
        ["EUR to USD to JPY with a 0.35% fee", "final yen after two conversions", "12480 euros into yen via dollars", "double currency conversion net of fee", "12480 欧元换日元，扣 0.35% 手续费"])

    def c6():
        import math
        return [round(math.log(2) / math.log(1.0425), 2)]
    one(6, [T("年化 4.25% 复利，本金翻一倍至少要多少年？保留两位小数。", tol=0.006)], c6, ["4.25%"],
        "Doubling time. ln2/ln(1.0425) = 16.6x.", "16.9",
        ["复利翻倍要几年 4.25%", "本金翻番所需年数", "ln2 除以 ln(1.0425)", "4.25% 的翻倍年限", "years to double at 4.25% compound"])

    def c7():
        base = 8999 / 24 + 8999 * 0.0045
        return [round(base, 2), round(8999 * 0.0045 * 24, 2)]
    one(7, [T("手机 8999 元分 24 期，每期手续费是 8999 的 0.45%，本金平均分摊，那每月要还多少？保留两位小数。", tol=0.006),
            T("比一次性付清一共多花多少钱？", tol=0.006)], c7, ["8999", "24 期", "0.45%"],
        "Instalment fees. 8999/24+8999*0.0045 = 415.45; total fees 971.89.", "374.96",
        ["8999 分 24 期每月多少", "分期手续费 0.45% 每月还款", "比全款多付的手续费总和", "手机分期月供和总手续费", "phone on 24 instalments with a 0.45% fee"])

    def c8():
        import math
        return [round(3.14159265 * 1.35 ** 2 * 2.8 * 1000)]
    mk("hyb-34358", sub="D0", turns=[T("A cylindrical water tank has a radius of 1.35 m and a height of 2.8 m. Using pi = 3.14159265, how many liters does it hold, to the nearest liter?", tol=0.6)],
       compute=c8, given=["1.35", "2.8", "3.14159265"], decoy="5698", notes="Cylinder volume. pi*1.35^2*2.8*1000 = 16032 L.",
       must=["calculator", "bash"], files=W(8), rc=1,
       alts=["tank volume in liters, r 1.35 m, h 2.8 m", "capacity of a cylinder with radius 1.35", "cylindrical tank litres nearest liter", "pi r^2 h for a 2.8 m tall tank", "圆柱水箱半径 1.35 米高 2.8 米容量"])

    def c9():
        inc = 23480
        return [(8000 - 5000) * 0.03 + (17000 - 8000) * 0.10 + (inc - 17000) * 0.20]
    one(9, [T("帮我算一下应缴税额：月应纳税所得额 23480 元，其中 5000 以内不交税，5000 到 8000 的部分按 3%，8000 到 17000 的部分按 10%，超过 17000 的部分按 20%。一共交多少？", tol=0.006)],
        c9, ["23480", "3%", "10%", "20%"], "Progressive tax. 90+900+1296 = 2286.", "4696",
        ["分段累进税额 23480", "五档累进税率应缴多少", "超过 17000 的部分 20% 怎么算", "月收入 23480 的税额", "progressive tax on 23480 with three brackets"])

    def c10():
        sub = 14 * 128.45 + 3 * 2310.80
        return [round(sub * 1.0825 * 0.97, 2), round(sub * 1.0825, 2)]
    one(10, [T("Total up these invoices for me: 14 items at $128.45 and 3 items at $2,310.80. Add 8.25% sales tax, then take 3% off the taxed total for paying early. What is due? Two decimals.", tol=0.006),
             T("What would it be without the early-payment discount?", tol=0.006)], c10, ["128.45", "2,310.80", "8.25%"],
        "Invoice total. subtotal 8730.70; *1.0825*0.97 and *1.0825.", "9100",
        ["invoice total with tax and early discount", "14 x 128.45 plus 3 x 2310.80 with tax", "amount due after 3% early-pay discount", "taxed total without discount", "两批发票合计加税再打九七折"])
