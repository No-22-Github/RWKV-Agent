"""D2 part a: the calculator rejects the needed syntax/function; recover via pow, awk or by hand (hyb-34331..34340)."""
from common import T, W, mk


def one(i, prompts, compute, given, note, decoy, ref, alts):
    mk("hyb-%d" % (34330 + i), sub="D2", turns=prompts, compute=compute, given=given, decoy=decoy, notes=note,
       must=["calculator", "bash"], max_calls={"calculator": 2}, files=W(i), rc=2, ref=ref, alts=alts)


def build():
    def c1():
        return [round(20000 * 1.05 ** 10, 2), round(20000 * 1.05 ** 15, 2)]
    one(1, [T("帮我算一下 20000*1.05^10 等于多少，保留两位小数，这是我一笔定期存款十年后的本息。"),
            T("那存十五年呢？也是两位小数。")], c1, ["20000", "1.05^10"],
        "Compound growth written with ^. 20000*1.05^10 = 32577.89; 15 years 41578.56. The calculator rejects ^ and points to pow.",
        "30000", (["awk 'BEGIN{printf \"%.2f %.2f\\n\", 20000*1.05^10, 20000*1.05^15}'"], "32577.89 41578.56"),
        ["定期存款 20000 元，年利率 5%，复利十年多少", "20000*1.05^10 的结果", "本金两万按 5% 复利存 10 年再存 15 年",
         "十年后本息合计（20000，5%，复利）", "20000 at 5% compounded for 10 years, then 15 years"])

    def c2():
        return [3 ** 5 + 2 ** 8 - 7 ** 3]
    one(2, [T("这道题的式子是 3**5 + 2**8 - 7**3，帮我算出结果。")], c2, ["3**5", "2**8", "7**3"],
        "Powers written with **. 243+256-343 = 156.", "10",
        (["awk 'BEGIN{print 3^5 + 2^8 - 7^3}'"], "156"),
        ["3**5 + 2**8 - 7**3 等于几", "算 3 的 5 次方加 2 的 8 次方减 7 的 3 次方", "式子 3**5+2**8-7**3 的值",
         "三个幂的加减结果", "evaluate 3**5 + 2**8 - 7**3"])

    def c3():
        import math
        return [math.factorial(10), 2 * math.factorial(9)]
    one(3, [T("班里 10 个同学站成一排拍照，一共有多少种不同的站法？"), T("如果其中小李和小王必须挨着站，又有多少种？")], c3,
        ["10 个", "小李", "小王"],
        "Permutations. 10! = 3628800; with two adjacent 2*9! = 725760. Factorial is not supported by the calculator.",
        "362880", (["awk 'BEGIN{f=1;for(i=2;i<=10;i++)f*=i; printf \"%d %d\\n\", f, f/10*2}'"], "3628800 725760"),
        ["10 个人排队有几种排法", "十位同学合影的排列数，再算两人相邻的情况", "10 人全排列，以及两人捆绑",
         "站成一排的方案数", "ways to line up 10 students, two of them adjacent"])

    def c4():
        import math
        return [math.comb(12, 4), math.comb(12, 4) - math.comb(10, 2)]
    one(4, [T("社团有 12 个人，要选 4 个人组成筹备小组，有多少种选法？"),
            T("如果其中有两个人闹矛盾，不能同时入选，那又有多少种？")], c4, ["12 个", "4 个", "两个人"],
        "Combinations. C(12,4) = 495; minus the 45 groups containing both feuding members = 450.",
        "11880", (["awk 'BEGIN{printf \"%d %d\\n\", 12*11*10*9/24, 12*11*10*9/24-45}'"], "495 450"),
        ["12 选 4 有几种组合", "十二个人里挑四人的方案数，再排除两人同组", "筹备小组选人方式", "C(12,4) 是多少，去掉两人同时入选",
         "choose a 4-person team from 12, minus teams with both rivals"])

    def c5():
        import math
        return [round(120 * math.sin(math.radians(35)), 2), round(120 * math.sin(math.radians(20)), 2)]
    one(5, [T("一段斜坡长 120 米，和水平面的夹角是 35 度，坡顶比坡底高多少米？保留两位小数。"),
            T("要是夹角改成 20 度，斜坡还是 120 米呢？")], c5, ["120", "35 度", "20 度"],
        "Right-triangle height with sine. 120*sin(35 deg) = 68.83; at 20 deg 41.04. The calculator has no trig functions.",
        "-51.4", (["awk 'BEGIN{p=atan2(0,-1); printf \"%.2f %.2f\\n\", 120*sin(35*p/180), 120*sin(20*p/180)}'"], "68.83 41.04"),
        ["斜坡 120 米倾角 35 度，垂直升高多少", "35 度的坡走 120 米爬升几米", "坡顶高度（斜长 120，35°）再算 20°",
         "斜面高度计算，保留两位小数", "a 120 m slope at 35 degrees: vertical rise, then at 20"])

    def c6():
        import math
        return [round(45 * math.tan(math.radians(32)) + 1.6, 2)]
    one(6, [T("我站在离教学楼 45 米的地方，抬头看楼顶的仰角是 32 度，我的眼睛离地 1.6 米，这栋楼大约多高？保留两位小数。")], c6,
        ["45 米", "32 度", "1.6"],
        "Building height with tangent. 45*tan(32 deg)+1.6 = 29.72.", "28.12",
        (["awk 'BEGIN{p=atan2(0,-1); a=32*p/180; printf \"%.2f\\n\", 45*sin(a)/cos(a)+1.6}'"], "29.72"),
        ["离楼 45 米仰角 32 度楼多高", "测楼高：距离 45 米，仰角 32°，眼高 1.6", "用仰角估算教学楼高度", "楼顶仰角 32 度，加上眼睛高度",
         "building height from 45 m away at 32 degrees plus eye level 1.6 m"])

    def c7():
        import math
        return [math.ceil(math.log2(50000))]
    one(7, [T("系统要给 50000 个用户各分配一个唯一的二进制编号，编号至少要几位？")], c7, ["50000"],
        "Bits needed. ceil(log2(50000)) = 16 (2^15 = 32768 < 50000 <= 65536 = 2^16). The calculator has ln and log10 but no log2.",
        "15", (["awk 'BEGIN{x=log(50000)/log(2); printf \"%.4f %d\\n\", x, (x==int(x))?x:int(x)+1}'"], "15.6096 16"),
        ["50000 个用户的编号要几位二进制", "二进制位数 log2(50000) 向上取整", "给五万人编号至少几比特", "唯一编号的最短二进制长度",
         "minimum bits for 50000 unique ids"])

    def c8():
        import math
        return [math.ceil(1234 / 48), math.ceil(1234 / 60)]
    one(8, [T("仓库有 1234 件产品要装箱，每箱最多装 48 件，至少需要几个箱子？"), T("如果换成每箱最多 60 件的大箱呢？")], c8,
        ["1234", "48", "60"],
        "Round-up division. ceil(1234/48) = 26; ceil(1234/60) = 21. The calculator has round but no ceil or floor.",
        "25", (["awk 'BEGIN{a=1234/48; b=1234/60; printf \"%d %d\\n\", (a>int(a))?int(a)+1:a, (b>int(b))?int(b)+1:b}'"], "26 21"),
        ["1234 件货每箱 48 件要几箱", "装箱最少箱数，再换 60 件一箱", "1234 除以 48 向上取整", "需要多少个箱子（可以不装满）",
         "boxes needed for 1234 items at 48 per box, then 60"])

    def c9():
        return [round(500 ** (1 / 3), 2)]
    one(9, [T("一个实心正方体铁块体积是 500 立方厘米，它的棱长是多少厘米？保留两位小数。")], c9, ["500"],
        "Cube root. 500^(1/3) = 7.94. There is no cbrt; pow(500, 1/3) or awk exp(log(500)/3) works.", "166.67",
        (["awk 'BEGIN{printf \"%.2f\\n\", exp(log(500)/3)}'"], "7.94"),
        ["体积 500 的正方体棱长", "500 立方厘米对应的边长", "开三次方 500", "正方体铁块边长保留两位小数",
         "edge of a cube with volume 500 cm3"])

    def c10():
        a, b = 84, 126
        import math
        return [a * b // math.gcd(a, b)]
    one(10, [T("两路公交同时从总站发车，一路每 84 分钟一班，另一路每 126 分钟一班，多少分钟后会再次同时发车？")], c10, ["84", "126"],
        "Least common multiple. lcm(84,126) = 252. The calculator has no gcd or lcm.", "10584",
        (["awk 'BEGIN{a=84;b=126;x=a;y=b;while(y){t=x%y;x=y;y=t}; print a*b/x}'"], "252"),
        ["84 和 126 的最小公倍数", "两路车下次同时发车是多少分钟后", "每 84 分钟一班和每 126 分钟一班的重合时间",
         "公交同时发车间隔", "buses every 84 and 126 minutes: when do they leave together again"])
