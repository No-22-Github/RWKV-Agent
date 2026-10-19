"""D2 part b (hyb-34341..34350)."""
from common import T, W, mk


def one(i, prompts, compute, given, note, decoy, ref, alts):
    mk("hyb-%d" % (34330 + i), sub="D2", turns=prompts, compute=compute, given=given, decoy=decoy, notes=note,
       must=["calculator", "bash"], max_calls={"calculator": 2}, files=W(i), rc=2, ref=ref, alts=alts)


def build():
    def c11():
        return [840 * 15 / 100 + 1250 * 8 / 100]
    one(11, [T("帮我算一下 840*15% + 1250*8% 是多少。")], c11, ["840*15%", "1250*8%"],
        "Percent signs in the expression. 126+100 = 226. A trailing % makes the calculator's parser fail (% is modulo there).",
        "22600", (["awk 'BEGIN{print 840*15/100 + 1250*8/100}'"], "226"),
        ["840 的 15% 加 1250 的 8%", "两个百分比相加：840*15% 和 1250*8%", "百分号写法的式子结果", "算 840*15%+1250*8%",
         "what is 15% of 840 plus 8% of 1250"])

    def c12():
        return [sum(i * i for i in range(1, 21))]
    one(12, [T("帮我算 1^2 + 2^2 + 3^2 + … + 20^2 的和是多少。")], c12, ["1^2", "20^2"],
        "Sum of squares written with ^. 20*21*41/6 = 2870.", "210",
        (["awk 'BEGIN{for(i=1;i<=20;i++)s+=i*i; print s}'"], "2870"),
        ["1 到 20 的平方和", "前二十个自然数平方相加", "1^2+2^2+…+20^2", "平方和公式的结果", "sum of the squares 1 to 20"])

    def c13():
        return [round(10000 * (1 + 0.06 / 12) ** 24, 2)]
    one(13, [T("理财产品年化 6%，按月复利，本金 10000 元，两年后的本息按 10000 * (1 + 0.06/12) ** 24 算，是多少？保留两位小数。")], c13,
        ["10000", "0.06/12", "** 24"],
        "Monthly compounding written with **. 10000*1.005^24 = 11271.60.", "11200",
        (["awk 'BEGIN{printf \"%.2f\\n\", 10000*(1+0.06/12)^24}'"], "11271.60"),
        ["月复利两年 10000 元年化 6%", "10000*(1+0.06/12)**24 的值", "理财两年后本息", "按月复利计算 24 期", "10000 at 6% monthly compounding for two years"])

    def c14():
        import math
        return [round(math.sqrt(7 ** 2 + 9 ** 2 - 2 * 7 * 9 * math.cos(math.radians(40))), 2)]
    one(14, [T("三角形两条边分别是 7 厘米和 9 厘米，夹角 40 度，第三条边有多长？保留两位小数。")], c14, ["7 厘米", "9 厘米", "40 度"],
        "Law of cosines. sqrt(49+81-126*cos40) = 5.79.", "11.4",
        (["awk 'BEGIN{p=atan2(0,-1);printf \"%.2f\\n\", sqrt(49+81-2*7*9*cos(40*p/180))}'"], "5.79"),
        ["两边 7 和 9 夹角 40° 求第三边", "余弦定理算第三边", "三角形边长计算保留两位", "夹角 40 度的三角形", "third side with sides 7, 9 and angle 40 degrees"])

    def c15():
        import math
        return [int(math.log2(100000)) + 1]
    one(15, [T("有 100000 个已经排好序的数据，用二分查找，最坏情况下要比较几次？")], c15, ["100000"],
        "Binary search worst case. floor(log2(100000))+1 = 17.", "16",
        (["awk 'BEGIN{x=log(100000)/log(2); printf \"%.4f %d\\n\", x, int(x)+1}'"], "16.6096 17"),
        ["十万条有序数据二分最多比较几次", "log2(100000) 取整加一", "二分查找最坏比较次数", "100000 个元素的二分查找", "worst-case comparisons of binary search over 100000 items"])

    def c16():
        import math
        return [math.factorial(8)]
    one(16, [T("圆桌上坐 9 个人，转一圈算同一种坐法，一共有多少种不同的坐法？")], c16, ["9 个人"],
        "Circular permutations. (9-1)! = 40320.", "362880",
        (["awk 'BEGIN{f=1;for(i=2;i<=8;i++)f*=i;print f}'"], "40320"),
        ["9 人围圆桌的排法", "圆排列 9 个人", "旋转算同一种，坐法数", "九个人围坐一桌", "seating 9 people at a round table"])

    def c17():
        import math
        return [math.comb(12, 5), math.comb(13, 5)]
    one(17, [T("What is 12 choose 5?"), T("And 13 choose 5?")], c17, ["12 choose 5", "13 choose 5"],
        "Binomial coefficients. C(12,5) = 792; C(13,5) = 1287.", "95040",
        (["awk 'BEGIN{print 12*11*10*9*8/120, 13*12*11*10*9/120}'"], "792 1287"),
        ["how many ways to pick 5 of 12", "12 choose 5 and then 13 choose 5", "binomial 12 over 5", "5-person committees from 12 people", "12 选 5 是多少，13 选 5 呢"])

    def c18():
        return [2 ** 31 - 1]
    one(18, [T("Can you compute 2^31 - 1 for me? I want the exact integer.")], c18, ["2^31"],
        "Largest signed 32-bit integer written with ^. 2147483647.", "2147483648",
        (["awk 'BEGIN{printf \"%d\\n\", 2^31-1}'"], "2147483647"),
        ["value of 2^31 - 1", "max int32 exact value", "two to the 31st minus one", "2^31-1 as an integer", "2 的 31 次方减 1"])

    def c19():
        import math
        return [math.factorial(7) // 4]
    one(19, [T("How many different ways can the letters of the word LETTERS be arranged?")], c19, ["LETTERS"],
        "Multiset permutations. 7!/(2!*2!) = 1260 (E twice, T twice).", "5040",
        (["awk 'BEGIN{f=1;for(i=2;i<=7;i++)f*=i;print f/4}'"], "1260"),
        ["arrangements of the letters in LETTERS", "distinct anagrams of LETTERS", "LETTERS 一词的字母排列数", "how many anagrams does LETTERS have", "number of orderings of L,E,T,T,E,R,S"])

    def c20():
        import math
        return [round(6 * math.sin(math.radians(70)), 2), round(6 * math.sin(math.radians(60)), 2)]
    one(20, [T("A 6 m ladder leans against a wall at 70 degrees to the ground. How high up the wall does it reach? Two decimals please."),
             T("And if I lower the angle to 60 degrees?")], c20, ["6 m", "70 degrees", "60 degrees"],
        "Ladder height with sine. 6*sin(70 deg) = 5.64; at 60 deg 5.20.", "2.05",
        (["awk 'BEGIN{p=atan2(0,-1);printf \"%.2f %.2f\\n\", 6*sin(70*p/180), 6*sin(60*p/180)}'"], "5.64 5.20"),
        ["ladder 6 m at 70 degrees reach height", "height reached by a 6 meter ladder", "wall height at 70° then 60°", "ladder angle problem two decimals", "6 米梯子靠墙 70 度能到多高"])
