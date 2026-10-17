"""calculator part 1: multi-step amounts, percentages, compound interest, splits."""
from common import mk

B = []


def b(f):
    B.append(f)
    return f


@b
def c01():
    def compute(files, wx):
        return {}, [[("num", round((5299 - 200) * 0.95, 2))]]
    mk("hyb-33629", sub="calc", desc="Coupon first, then member discount, two-decimal payable amount",
       turns=[{"p": "手机标价 5299 元，先用 200 元优惠券抵扣，再享受会员 95 折，实付多少钱？保留两位小数。", "tol": 0.006, "req": ["calculator"]}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "4844.5"}, rc=1,
       notes="(5299-200)*0.95 = 4844.05. Order matters: the other order gives 5299*0.95-200 = 4834.05.",
       alts=["5299 的手机，减 200 券后打 95 折，付多少", "优惠券 200 再 95 折，5299 元手机最终价格", "手机 5299，先抵 200 再 9.5 折，实付", "算一下手机实付：5299 元，200 元券，95 折，两位小数", "A 5299 yuan phone: 200 coupon first, then 5% off. Final price?"])


@b
def c02():
    def compute(files, wx):
        return {}, [[("num", round((4512960 - 3847200) / 3847200 * 100, 2))]]
    mk("hyb-33630", sub="calc", desc="Year-over-year revenue growth percentage, two decimals",
       turns=[{"p": "去年营收 3847200 元，今年 4512960 元，同比增长百分之多少？保留两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "14.75"}, rc=1,
       notes="(4512960-3847200)/3847200*100 = 17.3055... -> 17.31. Dividing by this year's figure gives 14.75 (decoy).",
       alts=["营收从 3847200 到 4512960，增幅多少百分点", "同比增速是多少（去年 3847200，今年 4512960）", "今年比去年增长了百分之几，两位小数", "3847200 增长到 4512960 的涨幅", "Revenue rose from 3,847,200 to 4,512,960. Growth in percent, 2 decimals?"])


@b
def c03():
    def compute(files, wx):
        v = 80000
        for _ in range(3):
            v = v * 1.0365
        return {}, [[("num", round(v, 2))]]
    mk("hyb-33631", sub="calc", desc="Three-year compound deposit principal plus interest",
       turns=[{"p": "存 80000 元，年利率 3.65%，每年利息滚入本金，存满 3 年后本息一共多少？保留两位小数。", "tol": 0.006, "req": ["calculator"]}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "88760"}, rc=1,
       notes="80000*1.0365^3 = 89083.63; simple interest would give 88760.",
       alts=["8 万元年息 3.65% 复利存 3 年到期本息", "80000 复利三年 3.65%，最终金额", "年化 3.65% 利滚利，三年后多少钱（80000 本金）", "复利计算：本金 80000，3.65%，3 年", "80,000 at 3.65% compounded yearly for 3 years: final amount?"])


@b
def c04():
    def compute(files, wx):
        return {}, [[("num", round(1386.40 * 1.10 / 7, 2))]]
    mk("hyb-33632", sub="calc", desc="Split a restaurant bill with a service charge among seven people",
       turns=[{"p": "聚餐账单 1386.40 元，另加 10% 服务费，7 个人 AA，每人付多少？保留两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "198.06"}, rc=1,
       notes="1386.40*1.1/7 = 217.8686 -> 217.87. Without the service charge: 198.06 (decoy).",
       alts=["账单 1386.40 加一成服务费七人平分", "7 人 AA，1386.40 元外加 10% 服务费，每人多少", "每人应付多少：总价 1386.40，服务费 10%，7 人", "聚餐 AA 计算，含 10% 服务费", "Bill 1386.40 plus 10% service, split 7 ways: each pays?"])


@b
def c05():
    def compute(files, wx):
        return {}, [[("num", round(18650 * 0.885, 2))], [("num", round(18650 * 2.5 * 0.8, 2))]]
    mk("hyb-33633", sub="calc", desc="Multi-turn pay calculation: net monthly pay, then a bonus after tax",
       turns=[{"p": "我月薪税前 18650，五险一金扣 11.5%，扣完剩多少？保留两位小数。", "tol": 0.006},
              {"p": "年终奖按 2.5 个月税前工资发，要扣 20% 的税，到手多少？也是两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "18650"}, rc=2,
       notes="Turn1: 18650*(1-0.115)=16505.25. Turn2: 18650*2.5*0.8 = 37300.",
       alts=["月薪 18650 扣 11.5% 剩多少", "税前 18650，五险一金 11.5%，到手", "扣掉 11.5% 后的月薪", "18650 减去 11.5% 是多少", "Salary 18650, 11.5% deducted: what remains?"])


@b
def c06():
    def compute(files, wx):
        gross = 3200 * 7.1873
        return {}, [[("num", round(gross - gross * 0.005, 2))]]
    mk("hyb-33634", sub="calc", desc="Currency exchange with a percentage fee charged in yuan",
       turns=[{"p": "我要换 3200 美元，汇率 7.1873，银行按换得人民币金额收 0.5% 手续费，最后到手多少人民币？保留两位小数。", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "22999.36"}, rc=1,
       notes="3200*7.1873 = 22999.36; fee 0.5% = 114.9968; net 22884.3632 -> 22884.36.",
       alts=["3200 美元按 7.1873 换，扣 0.5% 手续费", "换汇到手多少：3200 美元，汇率 7.1873，手续费 0.5%", "美元兑人民币 7.1873，换 3200，再扣千分之五", "到手人民币是多少，手续费 0.5%", "Exchange $3200 at 7.1873 minus a 0.5% fee in CNY: net?"])


@b
def c07():
    def compute(files, wx):
        return {}, [[("num", round(12500 * (1 + 0.042 * 1.5), 2))]]
    mk("hyb-33635", sub="calc", desc="English simple-interest loan repayment over 18 months",
       turns=[{"p": "A loan of 12,500 carries 4.2% simple interest per year. If I repay everything after 18 months, how much is the total repayment?", "tol": 0.006}],
       compute=compute, must=["calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "13,025"}, rc=1,
       notes="12500*(1+0.042*1.5) = 13,287.50. Using a full year of interest only gives 13,025 (decoy).",
       alts=["Total repayment on 12500 at 4.2% simple interest for 18 months?", "12,500 loan, 4.2% per year simple, 1.5 years: repay how much?", "Compute principal plus simple interest: 12500, 4.2%, 18 months", "How much do I owe after 18 months on a 12,500 loan at 4.2% simple?", "12500 元借款年息 4.2% 单利，18 个月后还多少"])
