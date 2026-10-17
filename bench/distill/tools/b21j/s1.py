from common import T, make

S = "smalltalk"


def build():
    def m(n, turns, trap="TR-NOTOOLNEED"):
        for t in turns:
            t["expect"]["require_active_no_call"] = True
        make("nt-%d" % n, sub="chat", tt=S, family="x", desc="Small talk %d" % n, turns=turns,
             notes={"ref": "Friendly short reply, no tool.", "why": "Open chat; checks a topical word."}, trap=trap)
    m(33155, [T("今天加班到九点才下班，累死了。", any_=["辛苦", "累", "休息", "早点", "抱抱", "心疼"], fmt=["zh"])], trap=None)
    m(33156, [T("Morning! Just finished my first cup of coffee, feeling human again.", any_=["morning", "Morning", "coffee", "Coffee", "good"], fmt=["en"])])
    m(33157, [T("谢谢你昨天帮我理清思路，今天开会顺利多了！", any_=["不客气", "太好了", "很高兴", "开心", "恭喜", "应该的", "为你高兴", "为你感到"], fmt=["zh"])], trap=None)
    m(33158, [T("你周末一般喜欢干什么呀？", any_=["我是", "AI", "助手", "没有周末", "没有身体", "不会累", "模型"], fmt=["zh"])], trap="TR-NOTOOLNEED")
    m(33159, [T("给我讲个短笑话吧，不要太冷。", any_=["：", ":", "？", "?", "，"], fmt=["zh"], maxc=500)])
    m(33160, [T("我养的猫今天把窗帘爬塌了，哈哈。", any_=["猫", "窗帘"], fmt=["zh"]),
              T("它好像一点都不内疚。", any_=["猫", "它", "内疚", "哈哈"], fmt=["zh"])])
    m(33161, [T("Feeling a bit stressed about my exam on Friday. Any quick words of encouragement?", any_=["exam", "Exam", "you've got this", "You've got this", "prepared", "breathe", "believe", "got this"], fmt=["en"])])
    m(33162, [T("你觉得下雨天适合干什么？", any_=["下雨", "雨", "咖啡", "书", "电影", "待在", "在家"], fmt=["zh"])])
    m(33163, [T("晚安啦，明天还要早起。", any_=["晚安", "好梦", "睡个好觉", "休息", "早点睡"], fmt=["zh"])], trap=None)
    m(33164, [T("你好！先随便聊两句：你是谁呀？", any_=["助手", "助理", "AI", "模型", "智能"], fmt=["zh"])], trap="TR-NOTOOLNEED")
    m(33165, [T("我今天终于把拖了三个月的报告交了！", any_=["恭喜", "太棒", "好棒", "厉害", "松了口气", "解脱", "了不起"], fmt=["zh"]),
              T("想奖励自己一顿好的，有什么建议？", any_=["火锅", "烧烤", "甜点", "大餐", "餐厅", "奖励", "吃", "寿司", "牛排"], fmt=["zh"])])
    m(33166, [T("Do you ever get tired of answering questions?", any_=["tired", "Tired", "don't", "do not", "AI", "no", "No"], fmt=["en"])])
    m(33167, [T("周一又到了，不想上班。", any_=["周一", "星期一", "理解", "懂", "加油", "慢慢", "小确幸", "撑", "休息"], fmt=["zh"])], trap=None)
