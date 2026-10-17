from common import T, make

U = "unit_convert"


def b(n, p, num, tol, sub_note, trap="TR-NOTOOLNEED", turns=None):
    make("nt-%d" % n, sub="unit", tt=U, family="x", desc=sub_note,
         turns=turns or [T(p, number=num, tol=tol)], notes={"ref": sub_note, "why": "Closed-form conversion."}, trap=trap)


def build():
    b(33142, "我在看一份美国食谱，要求烤箱预热到 350 华氏度。换成摄氏度大概是多少？", 176.67, 1.0, "350F to C")
    b(33143, "", None, None, "12.5 lb to kg then g", trap=None, turns=[
        T("A package weighs 12.5 pounds. How many kilograms is that? Round to two decimals.", number=5.67, tol=0.02),
        T("And in grams?", number=5670, tol=10)])
    b(33144, "高铁时速 300 公里，换算成米每秒是多少？", 83.33, 0.1, "300 km/h to m/s")
    b(33145, "我身高 5 英尺 10 英寸，等于多少厘米？", 177.8, 0.2, "5ft10in to cm")
    b(33146, "美国的汽油按加仑卖，一加仑（美制）大约是多少升？", 3.785, 0.01, "US gallon in litres", trap=None)
    b(33147, "How many seconds are there in 3.5 hours?", 12600, 1, "3.5 h to s")
    b(33148, "一块地 2.5 公顷，等于多少平方米？", 25000, 1, "2.5 ha to m2")
    b(33149, "跑马拉松全程 42.195 公里，换成英里大约是多少？保留一位小数。", 26.2, 0.1, "marathon in miles")
    b(33150, "房间面积 18 平方米，大约是多少平方英尺？取整即可。", 193.75, 1.5, "18 m2 to ft2")
    b(33151, "Convert -40 degrees Celsius to Fahrenheit.", -40, 0.01, "-40C to F", trap=None)
    b(33152, "", None, None, "two-turn", turns=[
        T("一杯水 250 毫升，换算成液体盎司（美制）大约是多少？", number=8.45, tol=0.1),
        T("那 1.5 升呢？", number=50.72, tol=0.5)])
    b(33153, "水箱容量 2400 升，合多少立方米？", 2.4, 0.001, "2400 L to m3")
    b(33154, "The flight is 8,200 km. How many miles is that, roughly (nearest whole number)?", 5095, 8, "8200 km to miles")
