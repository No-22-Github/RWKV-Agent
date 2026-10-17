from common import T, make

R = "rewrite_text"


def build():
    make("nt-33108", sub="rewrite", tt=R, family="x", desc="Turn rambling notes into bullet list, keep three items",
         turns=[T("把下面这段话整理成三条要点（用“-”开头），别漏掉数字：\n“这周我们要做的事情有这么几件：周三之前把库存盘点表发给仓库的邵敏，然后周四要核对一下上个月的退货单，一共有 37 张，最后周五下午三点开个小会讨论新品陈列。”",
                  inc=["邵敏", "37", "三点"], token=False, fmt=["zh"], any_=["- ", "-"])],
         notes={"ref": "Three bullets.", "why": "Keeps 邵敏, 37 and the Friday time."})
    make("nt-33109", sub="rewrite", tt=R, family="x", desc="Casual to formal English with name and time",
         turns=[T("Rewrite this in a formal tone for a client email, keep the details:\n\"hey Ms. Okonkwo, we gotta move our call from tue 3pm to thu 10am cuz the team is swamped. u ok with that?\"",
                  inc=["Okonkwo"], any_=["Thursday", "Thu"], exc=["gotta", "cuz", " u "], fmt=["en"])],
         notes={"ref": "Formal English; Thursday 10 am.", "why": "Slang removed."})
    make("nt-33110", sub="rewrite", tt=R, family="x", desc="Two-turn: polish then even shorter",
         turns=[T("润色一下这条朋友圈文案：“咖啡店新开业，大家来玩，买一送一，就这周末，地址在梧桐路19号。”",
                  inc=["梧桐路19号"], any_=["买一送一"], fmt=["zh"]),
                T("再短一点，二十个字以内。", inc=["买一送一"], fmt=["zh"], maxc=60)],
         notes={"ref": "Polish, then compress.", "why": "Key promo and address (turn1) kept; turn2 compact."})
    make("nt-33111", sub="rewrite", tt=R, family="x", desc="Translate Chinese menu line to English, keep price",
         turns=[T("翻译成英文，写在菜单上用：\n“招牌红烧牛肉面，慢炖六小时的牛腱子，配手工拉面和一颗溏心蛋，38元。”",
                  inc=["38"], any_=["beef", "Beef"], token=True, fmt=["en"])],
         notes={"ref": "English menu description with price 38.", "why": "Price token and beef."})
    make("nt-33112", sub="rewrite", tt=R, family="x", desc="Shorten product description keeping model and battery",
         turns=[T("Shorten this product blurb to under 25 words but keep the model name and battery life:\n\"Introducing the Aurelia X7 smart lamp, a beautifully designed lamp that you can control from your phone, which comes with a rechargeable battery that lasts for up to 14 hours and also has many colour modes.\"",
                  inc=["X7", "14"], token=True, fmt=["en"], maxc=220)],
         notes={"ref": "Short blurb.", "why": "Model X7 and 14 hours."})
    make("nt-33113", sub="rewrite", tt=R, family="x", desc="Soften refusal, keep alternative date",
         turns=[T("同事约我周五聚餐，我去不了，但想约下周二。帮我把这句话改得委婉有礼貌：“周五不行，我没空。下周二吧。”",
                  inc=["下周二"], any_=["抱歉", "不好意思", "遗憾", "恐怕", "可惜", "不巧"], exc=["我没空"], fmt=["zh"])],
         notes={"ref": "Polite decline.", "why": "Alternative day kept."})
    make("nt-33114", sub="rewrite", tt=R, family="x", desc="Translate then shorten in English",
         turns=[T("把这段话翻成英文：“明天上午九点在三楼会议室开项目启动会，请带上笔记本电脑。”", any_=["laptop", "Laptop", "notebook"], fmt=["en"], token=True),
                T("shorter please, one line.", any_=["laptop", "Laptop", "notebook"], fmt=["en"], maxc=160)],
         notes={"ref": "Translation then short English line.", "why": "Second turn English prompt."})
