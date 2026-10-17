from common import T, make

S = "stable_fact"


def build():
    make("nt-33136", sub="fact", tt=S, family="x", desc="Speed of light approx",
         turns=[T("真空中光速大约是多少？用 km/s 回答。", any_=["299792", "299,792", "30万", "300000", "300,000", "3×10"], fmt=["zh"])],
         notes={"ref": "~299792 km/s", "why": "accept approximations"})
    make("nt-33137", sub="fact", tt=S, family="x", desc="Largest ocean in English",
         turns=[T("Which ocean is the largest by area?", inc=["Pacific"])],
         notes={"ref": "Pacific", "why": "unique"}, trap=None)
    make("nt-33138", sub="fact", tt=S, family="x", desc="Days in a leap-year February",
         turns=[T("闰年的二月有几天？", inc=["29"], token=True, fmt=["zh"])],
         notes={"ref": "29", "why": "unique"}, trap=None)
    make("nt-33139", sub="fact", tt=S, family="x", desc="Author of Dream of Red Chamber",
         turns=[T("《红楼梦》通常认为是谁写的？后四十回一般认为是谁续的？", inc=["曹雪芹"], any_=["高鹗", "程伟元"], fmt=["zh"])],
         notes={"ref": "曹雪芹; 高鹗", "why": "standard attribution"})
    make("nt-33140", sub="fact", tt=S, family="x", desc="Color mixing blue and yellow",
         turns=[T("颜料里蓝色和黄色混在一起得到什么颜色？", inc=["绿"], fmt=["zh"])],
         notes={"ref": "绿色", "why": "unique"}, trap=None)
    make("nt-33141", sub="fact", tt=S, family="x", desc="Two-turn: currency of Japan then Korea",
         turns=[T("日本用的货币叫什么？", any_=["日元", "円", "JPY", "yen", "Yen"]),
                T("What about South Korea?", any_=["won", "Won", "KRW", "韩元", "韩圆"])],
         notes={"ref": "yen then won", "why": "unique"})
