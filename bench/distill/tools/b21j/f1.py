from common import T, make

S = "stable_fact"


def build():
    make("nt-33129", sub="fact", tt=S, family="x", desc="Boiling point of water at sea level",
         turns=[T("标准大气压下水的沸点是多少摄氏度？", inc=["100"], token=True, fmt=["zh"])],
         notes={"ref": "100", "why": "unique"}, trap=None)
    make("nt-33130", sub="fact", tt=S, family="x", desc="Capital of Australia",
         turns=[T("What is the capital of Australia? One word is fine.", inc=["Canberra"], exc=["Sydney is the capital", "capital is Sydney"])],
         notes={"ref": "Canberra", "why": "unique"})
    make("nt-33131", sub="fact", tt=S, family="x", desc="Chemical symbol of sodium and follow-up",
         turns=[T("钠的化学符号是什么？", inc=["Na"], token=True),
                T("那钾呢？", inc=["K"], token=True)],
         notes={"ref": "Na, K", "why": "chemistry"})
    make("nt-33132", sub="fact", tt=S, family="x", desc="Number of bones in adult human body",
         turns=[T("成年人体一般有多少块骨头？", inc=["206"], fmt=["zh"])],
         notes={"ref": "206", "why": "standard"})
    make("nt-33133", sub="fact", tt=S, family="x", desc="Who wrote Pride and Prejudice",
         turns=[T("《傲慢与偏见》的作者是谁？", any_=["简·奥斯汀", "简奥斯汀", "奥斯汀", "Austen", "Jane Austen"])],
         notes={"ref": "Jane Austen", "why": "unique"})
    make("nt-33134", sub="fact", tt=S, family="x", desc="Largest planet",
         turns=[T("太阳系里最大的行星是哪一颗？", inc=["木星"], fmt=["zh"])],
         notes={"ref": "木星", "why": "unique"}, trap=None)
    make("nt-33135", sub="fact", tt=S, family="x", desc="Year World War II ended",
         turns=[T("二战是哪一年结束的？再顺便说下是以什么事件为标志。", inc=["1945"], any_=["投降", "日本", "德国", "surrender"], fmt=["zh"])],
         notes={"ref": "1945, surrender", "why": "unique"})
