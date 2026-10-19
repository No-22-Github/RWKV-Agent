"""D0 part b (hyb-34361..34370)."""
import math

from common import T, W, mk


def one(i, prompts, compute, given, note, decoy, alts):
    must = ["calculator"] if i % 2 else ["calculator", "bash"]
    mk("hyb-%d" % (34350 + i), sub="D0", turns=prompts, compute=compute, given=given, decoy=decoy, notes=note,
       must=must, files=W(i), rc=1, alts=alts)


def build():
    def c11():
        i = 0.0035
        return [round(2000 * ((1 + i) ** 36 - 1) / i, 2)]
    one(11, [T("帮我算一下，每月月底存 2000 元，月利率 0.35%，存满 36 个月，到期一共多少钱？保留两位小数。", tol=0.006)], c11, ["2000", "0.35%", "36 个月"],
        "Ordinary annuity future value. 2000*((1.0035^36-1)/0.0035).", "72000",
        ["每月存 2000 月利率 0.35% 存 36 个月", "零存整取到期本息", "定投三年终值", "年金终值保留两位", "monthly deposits of 2000 for 36 months at 0.35%"])

    def c12():
        d = 468000 * 0.95
        return [round(d * 6 / 36, 2), round(d * 5 / 36, 2)]
    one(12, [T("设备原值 468000 元，残值率 5%，用年数总和法折旧，使用 8 年，第 3 年折旧额是多少？当年折旧 = (原值 - 残值) × 剩余年限 ÷ 年数总和。", tol=0.006),
             T("第 4 年呢？", tol=0.006)], c12, ["468000", "5%", "8 年"],
        "Sum-of-years-digits depreciation. 444600*6/36 = 74100; year 4: 444600*5/36 = 61750.", "55575",
        ["年数总和法第 3 年折旧", "原值 468000 残值率 5% 折旧", "8 年期设备折旧额", "第 4 年折旧多少", "SYD depreciation for year 3 of 8"])

    def c13():
        return [round(42.195 / ((3 * 3600 + 47 * 60 + 26) / 3600), 3)]
    one(13, [T("I ran a 42.195 km marathon in 3:47:26. What was my average speed in km/h, to three decimals?", tol=0.0006)], c13, ["42.195", "3:47:26"],
        "Average speed. 42.195/(13646/3600) = 11.131.", "11.13",
        ["marathon 3:47:26 average speed", "km/h for a 3 hour 47 minute marathon", "average speed over 42.195 km", "finish time to speed, three decimals", "全马 3 小时 47 分 26 秒平均时速"])

    def c14():
        import math
        v = [1284, 967, 1503, 1121, 876, 1390, 1042, 1218]
        m = sum(v) / len(v)
        return [round(math.sqrt(sum((x - m) ** 2 for x in v) / len(v)), 2)]
    one(14, [T("帮我算一下这组月销量的标准差（总体标准差），保留两位小数：1284, 967, 1503, 1121, 876, 1390, 1042, 1218。", tol=0.006)], c14, ["1284", "1218"],
        "Population standard deviation of eight values.", "190",
        ["八个月销量的总体标准差", "这组数据的离散程度", "销量标准差保留两位", "1284 967 1503 的标准差", "population std dev of 8 monthly sales"])

    def c15():
        return [round(1.35 * 9.5 * 30 * 0.5683, 2)]
    one(15, [T("空调功率 1.35 千瓦，每天开 9.5 小时，开 30 天，电价 0.5683 元一度，这个月空调电费多少？保留两位小数。", tol=0.006)], c15, ["1.35", "9.5", "0.5683"],
        "Electricity cost. 1.35*9.5*30*0.5683.", "218",
        ["空调一个月电费 1.35 千瓦", "电价 0.5683 乘用电量", "每天 9.5 小时 30 天的电费", "空调月度电费两位小数", "monthly AC electricity bill at 0.5683 per kWh"])

    def c16():
        i = 0.045 / 12
        n = 96
        a = 60000 * i / ((1 + i) ** n - 1)
        j = 0.035 / 12
        b = 60000 * j / ((1 + j) ** n - 1)
        return [round(a, 2), round(b, 2)]
    one(16, [T("I want to have $60,000 in 8 years. If the account pays 4.5% a year compounded monthly, what do I need to deposit at the end of each month? Two decimals.", tol=0.006),
             T("What if the rate is only 3.5%?", tol=0.006)], c16, ["60,000", "4.5%", "3.5%"],
        "Sinking-fund deposit. FV*i/((1+i)^96-1) for i=0.045/12 and 0.035/12.", "625",
        ["monthly deposit to reach 60000 in 8 years", "sinking fund at 4.5% monthly", "savings goal payment calculation", "what changes at 3.5%", "8 年攒 6 万每月存多少"])

    def c17():
        pi = 3.14159265
        area = pi * 3.2 ** 2 + 2 * pi * 3.2 * 1.2
        return [round(area * 85.6, 2)]
    one(17, [T("圆形水池直径 6.4 米，池壁高 1.2 米，池底和池壁内侧都要贴砖，每平方米 85.6 元（π 取 3.14159265），贴砖一共多少钱？保留两位小数。", tol=0.01)], c17,
        ["6.4", "1.2", "85.6"], "Tiling cost. (pi r^2 + 2 pi r h)*85.6.", "4000",
        ["池底加池壁贴砖费用", "直径 6.4 米水池贴砖", "圆柱内表面积乘单价", "水池贴砖预算两位小数", "tile cost for a round pool, floor plus wall"])

    def c18():
        import math
        a, b, c = 13.7, 21.4, 18.9
        s = (a + b + c) / 2
        return [round(math.sqrt(s * (s - a) * (s - b) * (s - c)), 2)]
    one(18, [T("三角形三条边分别是 13.7、21.4 和 18.9 厘米，帮我算一下面积，保留两位小数。", tol=0.01)], c18, ["13.7", "21.4", "18.9"],
        "Heron's formula.", "129",
        ["13.7 21.4 18.9 三边求面积", "海伦公式面积两位小数", "三角形面积边长已知", "三条边求面积", "area of a triangle with sides 13.7, 21.4, 18.9"])

    def c19():
        return [round(1249.99 * 0.875 * 1.0775 - 85, 2)]
    one(19, [T("A $1,249.99 laptop gets 12.5% off, then 7.75% tax is added to the discounted price, then I use an $85 rebate. What's my final cost? Two decimals.", tol=0.006)],
        c19, ["1,249.99", "12.5%", "7.75%", "$85"], "Discount, tax, rebate. 1249.99*0.875*1.0775-85.", "1093",
        ["laptop final cost after discount tax and rebate", "12.5% off then 7.75% tax minus 85", "net price of $1,249.99 laptop", "three-step price calculation", "笔记本折后加税再减返现"])

    def c20():
        p, r, n = 620000, 0.0395 / 12, 240
        m = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
        return [round(m, 2), round(m - p * r, 2)]
    one(20, [T("帮我算一下，房贷 620000 元，年利率 3.95%，20 年，等额本息，每月还多少？保留两位小数。", tol=0.006),
             T("其中第一个月还的本金是多少？", tol=0.02)], c20, ["620000", "3.95%", "20 年"],
        "First instalment split. M = P*r*(1+r)^n/((1+r)^n-1); principal part M-P*r.", "2040.83",
        ["62 万房贷 20 年月供", "首月本金多少", "等额本息 3.95% 月供", "第一期还款里的本金", "mortgage 620000 at 3.95% for 20 years"])
