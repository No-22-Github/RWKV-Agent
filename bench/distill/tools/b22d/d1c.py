"""D1 part c (ids 34321-34330)."""
from common import T, W, P, mk

DEC = "calling a tool"


def one(i, prompts, compute, given, note, **kw):
    mk("nt-%d" % (34300 + i), sub="D1", turns=prompts, compute=compute, given=given, decoy=DEC, notes=note,
       must=P(i), files=W(i), **kw)


def build():
    def c21():
        return [4500 * 0.38]
    one(21, [T("我手机电池容量 4500 毫安时，现在还剩 38% 的电，大概是多少毫安时？")], c21, ["4500", "38%"],
        "Battery left. 4500*0.38 = 1710.")

    def c22():
        return [48 * 0.75 - 5]
    one(22, [T("A shirt costs $48 and it's 25% off. I also have a $5 coupon to use after the discount. What do I pay?")], c22,
        ["48", "25%", "5"], "Discount then coupon. 48*0.75-5 = 31.")

    def c23():
        return [round(3.5 * 6.8, 2), round(3.5 * 6.8 + 2 * 5.5, 2)]
    one(23, [T("我买了 3.5 斤苹果，每斤 6.8 元，一共多少钱？"), T("再加 2 斤梨，每斤 5.5 元，现在一共多少？")], c23,
        ["3.5", "6.8", "5.5"], "Fruit totals. 23.8 then 34.8.")

    def c24():
        return [(540 - 480) / 480 * 100]
    one(24, [T("公司去年营收 480 万，今年 540 万，同比增长了百分之几？")], c24, ["480", "540"],
        "Growth rate. 60/480*100 = 12.5.")

    def c25():
        return [135 / 90 * 60]
    one(25, [T("If a train runs at 90 km/h, how many minutes does it need to cover 135 km?")], c25, ["90", "135"],
        "Travel time. 135/90*60 = 90.")

    def c26():
        return [66 / 24]
    one(26, [T("帮我算一下，一箱牛奶 24 盒，卖 66 元，平均一盒多少钱？")], c26, ["24", "66"],
        "Unit price. 66/24 = 2.75.")

    def c27():
        return [1840 / 9200 * 100]
    one(27, [T("我月薪 9200，社保和公积金一共扣了 1840，扣掉的占百分之几？")], c27, ["9200", "1840"],
        "Deduction share. 1840/9200*100 = 20.")

    def c28():
        return [(2 * 60 + 40) / 1.25]
    one(28, [T("I have 2 hours 40 minutes of video to get through. At 1.25x speed, how many minutes will it take?")], c28,
        ["2 hours 40", "1.25"], "Playback time. 160/1.25 = 128.")

    def c29():
        return [120 / 8, (120 - 40) / 8]
    one(29, [T("水箱里有 120 升水，每分钟放掉 8 升，全部放完要多少分钟？"), T("要是放到只剩 40 升就停，要放多少分钟？")], c29,
        ["120", "8 升", "40"], "Drain time. 15 then 10.")

    def c30():
        return [52 * 150]
    one(30, [T("帮我算一下，一年 52 周，我每周存 150 元，一年一共能存多少？")], c30, ["52", "150"],
        "Yearly saving. 52*150 = 7800.")
