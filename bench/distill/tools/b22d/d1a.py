"""D1 part a: mental arithmetic, no tool (ids 34301-34310)."""
from common import T, W, P, mk

DEC = "calling a tool"


def one(i, prompts, compute, given, note, **kw):
    cid = "nt-%d" % (34300 + i)
    mk(cid, sub="D1", turns=prompts, compute=compute, given=given, decoy=DEC, notes=note,
       must=P(i), files=W(i), **kw)


def build():
    def c1():
        return [round((48 - 6) / 48 * 100, 2)]
    one(1, [T("帮我算一下，班里 48 个学生，今天请假 6 个，出勤率是百分之几？")], c1, ["48", "6"],
        "Attendance rate. (48-6)/48*100 = 87.5.")

    def c2():
        return [36 * 4 - 20]
    one(2, [T("帮我算一下：一本书 36 元，买 4 本，再用一张 20 元的抵扣券，一共付多少钱？")], c2, ["36", "20"],
        "Four books minus a voucher. 36*4-20 = 124.")

    def c3():
        return [(72 + 85 + 90 + 78 + 95) / 5]
    one(3, [T("Can you work out the average of these test scores for me: 72, 85, 90, 78, 95?")], c3, ["72", "95"],
        "Mean of five scores. 420/5 = 84.")

    def c4():
        return [(12 * 60 + 20) - (8 * 60 + 45)]
    one(4, [T("帮我算算，高铁 8:45 发车，12:20 到站，一共坐了多少分钟？")], c4, ["8:45", "12:20"],
        "Train duration in minutes. 12:20-8:45 = 3h35m = 215.")

    def c5():
        return [7500 * 7, 7500 * 30]
    one(5, [T("我每天走 7500 步，帮我算一下一周能走多少步？"), T("那按一个月 30 天算呢？")], c5, ["7500", "30"],
        "Steps per week then per month. 52500 and 225000.")

    def c6():
        return [3 * 4.5 + 1.75]
    one(6, [T("I bought 3 notebooks at $4.50 each and one pen for $1.75. What did I spend in total?")], c6, ["4.50", "1.75"],
        "Total spend. 3*4.5+1.75 = 15.25.")

    def c7():
        return [185 / 5]
    one(7, [T("帮我算一下，一桶 5 升的食用油卖 185 元，平均每升多少钱？")], c7, ["185", "5 升"],
        "Unit price. 185/5 = 37.")

    def c8():
        return [240 * 0.75]
    one(8, [T("一件衬衫原价 240 元，现在打 75 折，帮我算一下现价是多少？")], c8, ["240", "75"],
        "Discounted price. 240*0.75 = 180.")

    def c9():
        return [250 / 12 * 30, 250 / 12 * 18]
    one(9, [T("A cookie recipe uses 250 g of flour for 12 cookies. How much flour do I need for 30 cookies?"),
            T("And for 18 cookies?")], c9, ["250", "12", "30", "18"],
        "Scaling a recipe. 250/12*30 = 625; 250/12*18 = 375.")

    def c10():
        return [267 / 3]
    one(10, [T("帮我算一下，三个人 AA，一共花了 267 元，每人付多少？")], c10, ["267"],
        "Equal split. 267/3 = 89.")
