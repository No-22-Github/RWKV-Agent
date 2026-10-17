from common import T, make


def build():
    R = "rewrite_text"
    make("nt-33101", sub="rewrite", tt=R, family="x", desc="Polish a rude-sounding delay notice, keep order number and date",
         turns=[T("帮我把下面这段话改得客气一点，别丢信息：\n“你们的订单 HZ-48213 要延期，从9月20日推到10月8日，没办法，仓库出了问题，自己看着办吧。”",
                  inc=["HZ-48213", "10月8日"], any_=["抱歉", "歉意", "不好意思", "对不起", "请见谅", "谅解"], exc=["自己看着办"], fmt=["zh"])],
         notes={"ref": "Rewrite politely; keep order number and new date; drop the rude closing.", "why": "Checks preserved entities and the removed rude phrase."})
    make("nt-33102", sub="rewrite", tt=R, family="x", desc="Shorten a meeting recap to one sentence",
         turns=[T("下面这段会议纪要太长了，压缩成一句话（不超过60字），保留负责人和截止日期：\n“周二下午的项目例会上，大家讨论了很久新版官网上线的事情，最后确定由陈静负责首页改版，设计稿要在11月5日前交付，测试由吴凯安排，具体时间另行通知，另外还提到了茶歇预算的问题，暂时没有结论。”",
                  inc=["陈静", "11月5日"], exc=["茶歇"], fmt=["zh"], maxc=140)],
         notes={"ref": "One sentence naming 陈静 and 11月5日, skipping the tea budget.", "why": "Entities kept; tea-break topic dropped."})
    make("nt-33103", sub="rewrite", tt=R, family="x", desc="Translate a short English notice into Chinese",
         turns=[T("Please translate this into Chinese:\n\"The warehouse at 27 Ferry Road will be closed on Saturday, 18 October for inventory. Deliveries scheduled for that day will be moved to Monday.\"",
                  inc=["Ferry", "18"], any_=["周一", "星期一", "礼拜一"], fmt=["zh"], token=True, exc=["will be closed"])],
         notes={"ref": "Chinese translation keeping Ferry Road, 18 Oct, Monday.", "why": "Monday spelled 周一/星期一/礼拜一."})
    make("nt-33104", sub="rewrite", tt=R, family="x", desc="Translate Chinese store notice to English, keep price",
         turns=[T("把这段通知翻译成英文，语气保持正式：\n“尊敬的会员，您好。本店将于10月12日至10月14日举办周年庆，全场满500元减80元，会员另享9折。”",
                  inc=["500", "80"], any_=["anniversary", "Anniversary"], fmt=["en"], token=True)],
         notes={"ref": "Formal English with 500 / 80.", "why": "Numbers as tokens; English output."})
    make("nt-33105", sub="rewrite", tt=R, family="x", desc="Two-turn: shorten then translate",
         turns=[T("帮我把这句话说得简短点：“由于近期供应商那边的原材料价格出现了比较明显的上涨，所以我们公司经过慎重考虑之后，决定从下个月1日开始把全部产品的价格上调6%。”",
                  inc=["6%"], fmt=["zh"], maxc=120),
                T("再翻译成英文给海外客户。", inc=["6%"], any_=["price", "prices", "Price", "Prices"], fmt=["en"])],
         notes={"ref": "Short zh sentence, then English version, 6% kept.", "why": "Second turn English."})
    make("nt-33106", sub="rewrite", tt=R, family="x", desc="Remove personal details from a complaint text",
         turns=[T("下面这段投诉我要贴到公开论坛，请把姓名、手机号、住址都去掉（可以用“某人”“电话略”代替），其余意思保留：\n“我叫钱立军，手机 13800015566，住在柳林路88号3单元502。上周三我在你们店买的电饭煲用了两天就不加热了，客服一直推脱。”",
                  inc=["电饭煲", "不加热"], exc=["钱立军", "13800015566", "柳林路", "3单元502"], fmt=["zh"])],
         notes={"ref": "Anonymised complaint.", "why": "Excludes four personal items; keeps product and fault."})
    make("nt-33107", sub="rewrite", tt=R, family="x", desc="Polish English email, keep amounts",
         turns=[T("Fix the grammar and make it sound more professional, keep all numbers:\n\"hi tom, i send you the invoice yesterday for 2,450 dollar but you not reply. pls pay before 30 October or we must add 3 percent late fee. thanks\"",
                  inc=["2,450", "30 October"], any_=["3%", "3 percent", "3 per cent"], fmt=["en"], exc=["pls "])],
         notes={"ref": "Polished email.", "why": "Keeps 2,450 / 30 October / 3%."})
