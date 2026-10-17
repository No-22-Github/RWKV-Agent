"""calculator part 2."""
from common import mk

B = []


def b(f):
    B.append(f)
    return f


@b
def c08():
    def compute(files, wx):
        return {}, [[("num", round((128.5 + 76.9 + 245.35) * 0.8 * 1.06, 2))]]
    mk("hyb-33636", sub="calc", desc="Three items, 20% off the subtotal, then 6% tax",
       turns=[{"p": "买了三样东西：128.5、76.9 和 245.35 元，整单打 8 折之后再加 6% 的税，一共付多少？保留两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "450.75"}, rc=1,
       notes="(128.5+76.9+245.35)=450.75; *0.8=360.6; *1.06=382.236 -> 382.24.",
       alts=["三件商品 128.5 76.9 245.35，八折加 6% 税", "整单 8 折后再收 6% 税，总价", "128.5+76.9+245.35 打八折再加税六个点", "含税总价：三件商品打 8 折", "Items 128.5, 76.9, 245.35 with 20% off, then 6% tax: total?"])


@b
def c09():
    def compute(files, wx):
        return {}, [[("num", round(17.6 / 0.8 - 49.9 / 2.5, 2))]]
    mk("hyb-33637", sub="calc", desc="Unit price comparison between two pack sizes",
       turns=[{"p": "超市大米：大包 2.5 公斤卖 49.9 元，小包 800 克卖 17.6 元。每公斤小包比大包贵多少元？保留两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "32.3"}, rc=1,
       notes="49.9/2.5 = 19.96 per kg; 17.6/0.8 = 22.00 per kg; difference 2.04.",
       alts=["大包 2.5kg 49.9 元，小包 800g 17.6 元，单价差", "每公斤差多少钱：2.5 公斤 49.9，800 克 17.6", "两种包装的每公斤价格相差多少", "大米小包每公斤贵多少", "Rice: 2.5 kg for 49.9 vs 800 g for 17.6; per-kg price gap?"])


@b
def c10():
    def compute(files, wx):
        a = (4350 + 286.7 + 99) / 3
        b_ = 4350 / 3 * 21 / 30 + (286.7 + 99) / 3
        return {}, [[("num", round(a, 2))], [("num", round(b_, 2))]]
    mk("hyb-33638", sub="calc", desc="Multi-turn shared-flat costs: equal split, then a pro-rated share for someone away",
       turns=[{"p": "三人合租，本月房租 4350，水电 286.7，网费 99，平均每人多少？保留两位小数。", "tol": 0.006},
              {"p": "如果甲出差 9 天没住（这个月按 30 天算），他的房租按天数折算只付 21/30，水电网费照旧三人平分，他这个月该付多少？两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "1585.57"}, rc=2,
       notes="Turn1: (4350+286.7+99)/3 = 1578.5667. Turn2: 4350/3*21/30 + 385.7/3 = 1015 + 128.5667 = 1143.5667.",
       alts=["三人合租总费用平均每人多少", "房租 4350 水电 286.7 网费 99 三人平摊", "每人分摊多少钱，三人合租", "合租费用人均", "Three flatmates split rent 4350, utilities 286.7 and internet 99: each pays?"])


@b
def c11():
    def compute(files, wx):
        return {}, [[("num", round(678 / 0.85, 2))]]
    mk("hyb-33639", sub="calc", desc="Work back from a discounted price to the original",
       turns=[{"p": "一件衣服打折后 678 元，正好是原价的 85%，原价是多少？保留两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-SIGN"], decoys={"TR-SIGN": "576.3"}, rc=1,
       notes="678/0.85 = 797.647 -> 797.65. Multiplying 678*0.85 = 576.3 is the decoy.",
       alts=["折后价 678 是原价的八五折，原价多少", "原价是多少：现价 678，为原价 85%", "反推原价，现价 678 元占 85%", "678 元对应原价的 85%，求原价", "A coat costs 678 after discount, which is 85% of list price. List price?"])


@b
def c12():
    def compute(files, wx):
        v = 36500
        for _ in range(4):
            v = v * 1.0218
        return {}, [[("num", round(v, 2))]]
    mk("hyb-33640", sub="calc", desc="Four-year compound growth of a deposit at 2.18%",
       turns=[{"p": "孩子的教育金账户现有 36500 元，年收益率 2.18%，收益每年转入本金，4 年后会有多少？保留两位小数。", "tol": 0.006, "req": ["calculator"]}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "39682.8"}, rc=1,
       notes="36500*1.0218^4 = 39788.40. Simple interest gives 39682.80 (decoy).",
       alts=["36500 元年化 2.18% 复利 4 年", "教育金 36500，每年 2.18% 利滚利，四年后金额", "4 年后账户余额，年收益 2.18%，复利", "复利终值：36500，2.18%，4 年", "36,500 growing at 2.18% a year compounded for 4 years?"])


@b
def c13():
    def compute(files, wx):
        return {}, [[("num", round(14 * 23.45 * 1.0725, 2))], [("num", round(3 * 23.45 * 1.0725, 2))]]
    mk("hyb-33641", sub="calc", desc="English multi-turn: total with sales tax, then refund of three returned items",
       turns=[{"p": "I bought 14 identical items at $23.45 each, and 7.25% sales tax applies. What did I pay in total? Round to cents."},
              {"p": "If I return 3 of them, how much do I get back, tax included? Round to cents."}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "70.35"}, rc=2,
       notes="Turn1: 14*23.45*1.0725 = 352.10175 -> 352.10. Turn2: 3*23.45*1.0725 = 75.450375 -> 75.45.",
       alts=["14 items at $23.45 with 7.25% tax: total paid", "Total cost of 14 x 23.45 plus 7.25% tax", "What's my total for fourteen $23.45 items including tax at 7.25%?", "Tax-inclusive total, 14 items 23.45 each, tax 7.25%", "买了 14 件 23.45 美元的东西，税率 7.25%，一共多少"])


@b
def c14():
    def compute(files, wx):
        return {}, [[("num", round((89 - 63.4) / 89 * 100, 2))]]
    mk("hyb-33642", sub="calc", desc="Gross margin versus markup",
       turns=[{"p": "一件商品进价 63.4 元，卖 89 元，毛利率是多少个百分点？毛利率指毛利占售价的比例，保留两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "40.38"}, rc=1,
       notes="(89-63.4)/89*100 = 28.764 -> 28.76. Markup on cost (40.38) is the decoy.",
       alts=["进价 63.4 售价 89 的毛利率", "毛利占售价的比例是多少，进价 63.4，卖 89", "算毛利率：成本 63.4，售价 89", "利润率（占售价）是多少", "Cost 63.4, price 89: gross margin as a percent of price?"])
