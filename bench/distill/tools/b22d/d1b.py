"""D1 part b (ids 34311-34320)."""
from common import T, W, P, mk

DEC = "calling a tool"


def one(i, prompts, compute, given, note, **kw):
    mk("nt-%d" % (34300 + i), sub="D1", turns=prompts, compute=compute, given=given, decoy=DEC, notes=note,
       must=P(i), files=W(i), **kw)


def build():
    def c11():
        return [50 - 2.5 * 12]
    one(11, [T("帮我算一下，一瓶水 2.5 元，我买了 12 瓶，给了收银员 50 元，应该找回多少？")], c11, ["2.5", "12", "50"],
        "Change due. 50-2.5*12 = 20.")

    def c12():
        return [36 / 480 * 100]
    one(12, [T("My car used 36 liters of fuel over 480 km. What's the consumption per 100 km, in liters?")], c12, ["36", "480"],
        "Fuel consumption. 36/480*100 = 7.5.")

    def c13():
        return [240 * (1 - 0.35) - 60]
    one(13, [T("仓库有 240 箱货，上午发走了 35%，下午又发走 60 箱，现在还剩多少箱？")], c13, ["240", "35%", "60"],
        "Stock left. 240*0.65-60 = 96.")

    def c14():
        return [(3200 + 180 + 100) / 3, (3200 + 180 + 100) / 2]
    one(14, [T("三个人合租，房租 3200，水电 180，网费 100，平摊的话每人多少钱？"), T("如果其中一个人出差不住，只由剩下两个人摊呢？")],
        c14, ["3200", "180", "100"], "Shared cost. 3480/3 = 1160; 3480/2 = 1740.")

    def c15():
        return [64 * 0.15]
    one(15, [T("Quick one: what's a 15% tip on a $64 dinner bill?")], c15, ["15%", "64"],
        "Tip. 64*0.15 = 9.6.")

    def c16():
        return [32 / 5, 32 / 5 * 10]
    one(16, [T("帮我算一下，我跑了 5 公里，用了 32 分钟，平均每公里用几分钟？"), T("按这个配速跑 10 公里要多少分钟？")], c16, ["5 公里", "32"],
        "Pace then 10 km time. 32/5 = 6.4; 64.")

    def c17():
        return [8.5 * 4]
    one(17, [T("院子里有一个长方形花坛，长 8.5 米，宽 4 米，面积是多少平方米？")], c17, ["8.5", "4 米"],
        "Rectangle area. 8.5*4 = 34.")

    def c18():
        return [45 * 12, 620 - 45 * 12]
    one(18, [T("I read 45 pages a day. How many pages is that over 12 days?"),
             T("My book has 620 pages. How many are left after those 12 days?")], c18, ["45", "12", "620"],
        "Pages read, then left. 540 and 80.")

    def c19():
        return [round(150 / 35, 1)]
    one(19, [T("帮我算一下，库存还有 150 件，每周大概卖 35 件，能卖几周？保留一位小数。", tol=0.05)], c19, ["150", "35"],
        "Weeks of stock. 150/35 = 4.2857 -> 4.3.")

    def c20():
        return [round((92 + 88 + 85) / 3, 2)]
    one(20, [T("这学期语文 92、数学 88、英语 85，帮我算一下三科平均分，保留两位小数。")], c20, ["92", "88", "85"],
        "Mean of three. 265/3 = 88.33.")
