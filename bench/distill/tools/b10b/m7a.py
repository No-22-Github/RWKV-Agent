"""b10b M7 (v1.4 §3.7) part A: official page vs second-hand page that disagree. 28 web + 12 hybrid."""
import json
from common import revised
NOEXC = set(['hyb-8022', 'hyb-8023', 'hyb-8024', 'hyb-8026', 'hyb-8028', 'hyb-8029', 'hyb-8032', 'web-8036', 'web-8037', 'web-8038', 'web-8039', 'web-8040', 'web-8041', 'web-8042', 'web-8043', 'web-8045', 'web-8048', 'web-8049', 'web-8051', 'web-8054', 'web-8055', 'web-8057', 'web-8059', 'web-8060', 'web-8063'] + ["web-8046"])
write_case = revised({'hyb-8022': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'hyb-8023': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'hyb-8024': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'hyb-8026': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'hyb-8028': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'hyb-8029': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'hyb-8032': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8036': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8037': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8038': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8039': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8040': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8041': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8042': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8043': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8045': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8048': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8049': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8051': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8054': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8055': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8057': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8059': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8060': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8063': 'S5：去掉旧值排除项——三遍老师都按「第三方页面写的旧值 X 已过时、以官网为准」解释旧值，被排除项误判；正确值仍是必含项，不会放过错答。', 'web-8046': 'S5：query_match 由「滨江市住房公积金」缩为「滨江」——老师的搜索词把城市和「住房公积金」分开写，三遍搜索全部零结果；另去掉旧值排除项（同上）。', 'web-8056': 'S5：词表补句首大写 Three years / Three-year——老师写「Three years on the machine」被判挂。'})

CASES = []


def phr(items):
    assert len(items) == 5
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, x) for i, x in enumerate(items))


def S(cid, fam, q, prompt, off, sec, rx, v, anys, exc, ref, why, kind="lookup_value", files=None,
      vcode=None, sec_first=True, maxc=600, trap="TR-WEBSTALE"):
    """off/sec: (url, title, snippet, content, date). rx: regex with one group over the
    official content that must yield v. anys: output_contains_any list. exc: excludes."""
    CASES.append(locals().copy())


# web scenario allows only these task_type values; hybrid uses local_first
def ttype(c):
    if c["cid"].startswith("hyb"):
        return "local_first"
    return "latest_version" if c["kind"] == "latest_version" else "lookup_value"


def run_vcode(c):
    if not c["vcode"]:
        return None
    import re
    ns = {"re": re, "files": c["files"], "off": c["off"][3]}
    exec(c["vcode"], ns)
    return ns["val"]


def build(c):
    cid = c["cid"]
    def pg(p):
        url, title, snip, content, date = p
        key = url.split("://", 1)[1]
        return {"query_match": c["q"], "url_match": key, "url": url, "title": title,
                "snippet": snip, "content": content, "published_at": date}
    offp = pg(c["off"])
    secs = [pg(p) for p in c["sec"]]
    web = (secs + [offp]) if c["sec_first"] else ([offp] + secs)
    # self-checks
    import re
    if c["vcode"]:
        assert run_vcode(c) == c["v"], (cid, "vcode")
    else:
        m = re.search(c["rx"], c["off"][3])
        assert m and m.group(1) == c["v"], (cid, "rx")
    assert any(a in c["ref"] for a in c["anys"]), (cid, "ref misses any")
    assert not any(e in c["ref"] for e in c["exc"]), (cid, "ref hits excludes")
    assert len(c["ref"]) <= 560, (cid, len(c["ref"]))
    for e in c["exc"]:
        assert e not in c["off"][3], (cid, "exclude in official page", e)
    assert not any(a in e for a in c["anys"] for e in c["exc"]), (cid, "any inside exclude")
    decoy = c["exc"][0]
    if cid in NOEXC:
        c["exc"] = []
    expect = {"output_contains_any": c["anys"], "output_excludes": c["exc"],
              "required_tools": ["web_fetch"], "max_output_chars": c["maxc"]}
    if not c["exc"]:
        del expect["output_excludes"]
    files = c["files"] or {}
    off_url = c["off"][0]
    if c["vcode"]:
        body = "files = case[\"files\"]\n" + c["vcode"].strip("\n") + "\nassert val == %r\n" % c["v"]
    else:
        body = "m = re.search(%r, off)\nassert m and m.group(1) == %r\n" % (c["rx"], c["v"])
    verify = '''
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == %r][0]["content"]
%sprint(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (off_url, body, json.dumps(c["anys"], ensure_ascii=False))
    notes = '''
## Traps
- %s: 搜索结果里的二手页（%s）给出 %s，与官方页不一致；官方页（%s，%s）给出 %s。

## Reference solution
1. 搜索题面里的对象：结果里有二手页和官方页。
2. 抓取官方页 %s，读出 %s。%s
终答示例：%s

## Why the answer is unique
官方页是该事实的一手来源且日期更新或更具体；二手页是转述或早于官方更新，所以 %s 才是答案，%s 是被取代 / 转述错误的值。%s
''' % (c["trap"], c["sec"][0][0], " / ".join(c["exc"]), c["off"][0], c["off"][4], c["v"], c["off"][0], c["v"],
       ("同时读本地文件取得对象信息（文件第一行就是决定对象的那一行）。" if files else ""), c["ref"], c["v"], " / ".join(c["exc"]), c["why"])
    tid = "hybrid" if cid.startswith("hyb") else "web"
    write_case(cid,
        desc=c["why"].split("。")[0] + "（官方页与二手页冲突，以官方为准）",
        task_type=ttype(c), family="fam-%s-b10b-%s-01" % (cid[:3], c["fam"]), level="L1",
        ref_calls=3 if files else 2, traps=[c["trap"]], decoys={c["trap"]: decoy}, axes=["VER"],
        web=web, files=files, turns=[{"prompt": c["prompt"], "expect": expect}], verify=verify, notes=notes + phr(PH[cid]))

# ---- web zh: policy / hours / fares / parameters
S("web-8036", "tierpower", "岚城",
  "岚城居民用电阶梯电价，第二档是从每月多少度开始算的？",
  ("https://www.lanchengpower.cn/tariff/residential", "岚城供电 | 居民阶梯电价执行标准", "居民生活用电阶梯档次与电价。",
   "# 居民阶梯电价执行标准\n\n2026 年 7 月 1 日起执行。\n\n- 第一档：月用电量 0—260 度，0.52 元/度\n- 第二档：月用电量 261—420 度，0.57 元/度\n- 第三档：月用电量 420 度以上，0.82 元/度\n", "2026-07-01"),
  [("https://www.lcdaily.cn/news/2026/electricity-tier", "岚城日报：电价阶梯怎么算", "第二档从每月 231 度起。",
    "# 岚城电价阶梯怎么算\n\n2025 年 12 月。市民问得最多的是第二档：目前第一档为月用电 230 度以内，第二档从 231 度起算。\n", "2025-12-18")],
  r"第二档：月用电量 (\d+)—", "261", ["261 度", "261度", "第二档从 261", "261 度起"], ["231 度", "231度"],
  "第二档从每月 261 度起算（261—420 度），依据是岚城供电 2026 年 7 月 1 日起执行的官方标准；去年底的新闻报道用的是旧口径。",
  "官方标准 2026-07-01 起执行并给出区间，新闻稿是去年 12 月的旧口径。"[:200], kind="policy_value"[:20] if False else "policy_value")
S("web-8037", "museumhours", "望潮",
  "望潮博物馆周末几点闭馆？想下午去逛，别白跑。",
  ("https://www.wangchao-museum.cn/visit", "参观指南 | 望潮博物馆", "开放时间、门票与交通。",
   "# 参观指南\n\n更新于 2026-09-05。\n\n**开放时间**：周二至周日 9:00—17:30（17:00 停止入馆），周一闭馆。\n夏季延时（7—8 月）已于 8 月 31 日结束，9 月 1 日起恢复常规时间。\n", "2026-09-05"),
  [("https://www.xiaoyou-travel.cn/notes/wangchao", "周末去望潮博物馆，这些你要知道", "周末可以逛到晚上 8 点，夜场很美。",
    "# 周末去望潮博物馆\n\n七月份去的，周末开到晚上 8 点，晚饭前后人少，拍照很美。\n", "2026-07-20")],
  r"周二至周日 9:00—(\d+:\d+)", "17:30", ["17:30", "17 点半", "下午 5 点半", "下午5点半", "五点半"], ["晚上 8 点", "晚上8点", "20:00", "八点"],
  "周末（周二至周日）17:30 闭馆，17:00 后停止入馆，依据是望潮博物馆官网参观指南；夏季延时到 8 点的安排 8 月底就结束了。",
  "官网参观指南更新于 9 月，写明夏季延时已结束；游记是 7 月的夏季安排。", kind="opening_hours")
S("web-8038", "ferryfare", "鹭岛轮渡",
  "鹭岛轮渡现在成人单程票价多少钱？",
  ("https://www.ludao-ferry.cn/fares", "票价公告 | 鹭岛轮渡", "鹭岛轮渡客运票价。",
   "# 票价公告\n\n自 2026 年 8 月 15 日起：成人单程 22 元，儿童（1.2—1.5 米）11 元，1.2 米以下免票。往返票不打折。\n", "2026-08-10"),
  [("https://tieba.example-forum.cn/p/ludao-ferry", "鹭岛轮渡多少钱？求攻略", "成人单程 18 元，学生半价。",
    "# 鹭岛轮渡多少钱？\n\n楼主：去年国庆坐过，成人单程 18 元，学生半价，往返 30 元。\n\n回复：对的，18 块。\n", "2025-10-09"),
   ("https://www.lvyou-wiki.cn/ludao", "鹭岛旅游百科", "到岛交通：轮渡成人 20 元。",
    "# 鹭岛\n\n交通：轮渡成人单程 20 元（2024 年数据）。\n", "2024-06-01")],
  r"成人单程 (\d+) 元", "22", ["22 元", "22元", "二十二元"], ["18 元", "18元", "20 元", "20元", "30 元"],
  "成人单程票价 22 元（儿童 11 元），依据是鹭岛轮渡官网 2026 年 8 月 15 日起执行的票价公告；论坛和百科里的价格是旧数据。",
  "官方公告给出自 2026-08-15 起的现行价，论坛和百科是 2024、2025 年的数据。", kind="price_value", sec_first=True)
S("web-8039", "libraryloan", "云港市图书馆",
  "云港市图书馆的普通图书一次能借多少天？",
  ("https://www.yungang-lib.cn/rules/borrow", "借阅规则 | 云港市图书馆", "读者证借阅册数、期限与续借。",
   "# 借阅规则\n\n2026 年 9 月 1 日修订。\n\n普通图书：每证最多借 10 册，借期 45 天，可续借一次 21 天。期刊：借期 15 天，不可续借。\n", "2026-09-01"),
  [("https://www.zhihu-like.cn/q/library-rules", "云港图书馆办证借书攻略", "普通图书借期 30 天。",
    "# 办证借书攻略\n\n2024 年整理：云港市图书馆普通图书最多借 8 册，借期 30 天，可续借 15 天。\n", "2024-11-02")],
  r"借期 (\d+) 天，可续借一次", "45", ["45 天", "45天", "四十五天"], ["30 天", "30天"],
  "普通图书借期 45 天（可续借一次 21 天），依据是云港市图书馆官网 2026 年 9 月 1 日修订的借阅规则；2024 年的攻略写的是旧规定。",
  "官网借阅规则 2026-09-01 修订，攻略是 2024 年的整理。", kind="policy_value")
S("web-8040", "phonebattery", "Lumo X5",
  "Lumo X5 手机的电池容量是多少毫安时？",
  ("https://www.lumo-mobile.cn/x5/specs", "Lumo X5 技术规格", "Lumo X5 官方规格参数。",
   "# Lumo X5 技术规格\n\n屏幕：6.7 英寸 AMOLED\n处理器：Lumo S3\n电池：5200 mAh（典型值），支持 67W 快充\n重量：201 g\n", "2026-08-20"),
  [("https://www.shumazhijia.cn/review/lumo-x5", "Lumo X5 首发评测", "电池 4800mAh，续航表现一般。",
    "# Lumo X5 首发评测\n\n发布前爆料版本电池为 4800mAh，我们拿到的工程机续航一般。\n", "2026-07-30")],
  r"电池：(\d+) mAh", "5200", ["5200 mAh", "5200mAh", "5200 毫安", "5200毫安", "5200 mah"], ["4800"],
  "Lumo X5 电池容量 5200 mAh（典型值），依据是 Lumo 官网的技术规格页；评测引用的是发布前爆料数据。",
  "官网规格页是产品参数的一手来源；评测引用的是发布前爆料版本。", kind="spec_value", sec_first=False)
S("web-8041", "airbaggage", "海燕航空",
  "海燕航空经济舱现在能免费托运多少公斤行李？",
  ("https://www.haiyan-air.cn/service/baggage", "行李规定 | 海燕航空", "托运与手提行李额度。",
   "# 行李规定\n\n2026 年 9 月 15 日起适用。\n\n经济舱免费托运行李额：国内航线 20 公斤，国际航线 23 公斤。手提行李 1 件，不超过 8 公斤。\n", "2026-09-10"),
  [("https://www.feixing-blog.cn/haiyan-baggage", "海燕航空行李攻略", "经济舱国内免费托运 15 公斤。",
    "# 海燕航空行李攻略\n\n海燕航空经济舱国内免费托运 15 公斤，超出每公斤按票价 1.5% 收费。\n", "2025-03-14")],
  r"国内航线 (\d+) 公斤", "20", ["20 公斤", "20公斤", "20 kg", "20kg", "20 千克"], ["15 公斤", "15公斤", "15 kg", "15kg"],
  "国内航线经济舱可免费托运 20 公斤（国际 23 公斤），依据是海燕航空官网 9 月 15 日起适用的行李规定；博客写的是旧标准。",
  "官网行李规定标明适用日期 2026-09-15，博客是 2025 年的攻略。", kind="policy_value")
S("web-8042", "expocal", "东港国际家居展",
  "东港国际家居展今年几号开幕？",
  ("https://www.dgexpo-home.cn/2026", "东港国际家居展 2026 | 官方网站", "展期、展馆与参观登记。",
   "# 东港国际家居展 2026\n\n展期：2026 年 11 月 6 日—9 日\n地点：东港国际会展中心 3、4 号馆\n公告（2026-09-02）：因场馆档期调整，开幕日期已顺延，以本页展期为准。\n", "2026-09-02"),
  [("https://www.huizhan-news.cn/a/dg-home", "东港家居展定档 10 月", "东港国际家居展 10 月 23 日开幕。",
    "# 东港家居展定档\n\n组委会此前透露，今年东港国际家居展将于 10 月 23 日开幕，为期四天。\n", "2026-06-12")],
  r"展期：2026 年 (\d+ 月 \d+) 日", "11 月 6", ["11 月 6 日", "11月6日", "11 月 6 号", "2026-11-06", "11 月 6"], ["10 月 23", "10月23"],
  "今年开幕日期是 11 月 6 日（展期 11 月 6—9 日），依据是展会官网 9 月 2 日的公告；此前的消息已经过时。",
  "官网 9 月公告明确变更了开幕日期，新闻稿是 6 月的旧消息。", kind="event_date")
S("web-8043", "parcelsurcharge", "迅达快递",
  "迅达快递的大件附加费，是从单件多少公斤起收的？",
  ("https://www.xunda-express.cn/price/surcharge", "附加费说明 | 迅达快递", "超重、超长附加费标准。",
   "# 附加费说明\n\n2026 年 8 月 1 日生效。\n\n单件超过 25 公斤按大件收取附加费 12 元/件；单边超过 120 厘米同样按大件处理。\n", "2026-07-28"),
  [("https://www.wangdian-help.cn/xunda", "迅达快递价格表整理", "超过 30 公斤收大件费。",
    "# 迅达快递价格表整理\n\n网点老板整理：迅达单件超过 30 公斤收大件附加费，10 元/件。\n", "2025-08-21")],
  r"单件超过 (\d+) 公斤", "25", ["25 公斤", "25公斤", "25 kg", "25kg", "25 千克"], ["30 公斤", "30公斤", "30 kg", "30kg"],
  "单件超过 25 公斤起按大件收附加费（12 元/件），依据是迅达快递官网 8 月 1 日生效的附加费说明；网点整理的是旧标准。",
  "官网附加费说明有生效日期 2026-08-01，网点整理是 2025 年的旧表。", kind="policy_value", sec_first=False)
S("web-8044", "routerwarranty", "Tarn AX6",
  "Tarn AX6 路由器官方保修期是多长？",
  ("https://www.tarn-net.cn/support/ax6/warranty", "Tarn AX6 保修政策", "Tarn AX6 整机与配件保修。",
   "# Tarn AX6 保修政策\n\n自 2026 年 3 月起售出的 AX6：整机保修 36 个月，电源适配器保修 6 个月。\n", "2026-03-01"),
  [("https://club.example-bbs.cn/t/tarn-ax6", "Tarn AX6 入手体验", "保修 12 个月，坏了找商家。",
    "# 入手体验\n\n保修 12 个月，坏了找商家换。路由器用着还行。\n", "2026-04-02"),
   ("https://www.zhidemai-like.cn/deal/ax6", "Tarn AX6 618 好价", "整机保修 24 个月。",
    "# 618 好价\n\n商品页写的是整机保修 24 个月，到手价 329。\n", "2026-06-10")],
  r"整机保修 (\d+) 个月", "36", ["36 个月", "36个月", "三年", "3 年", "3年"], ["12 个月", "12个月", "24 个月", "24个月"],
  "整机保修 36 个月（电源适配器 6 个月），依据是 Tarn 官网的保修政策页；论坛和促销页的说法不是官方口径。",
  "官方保修页对整机和配件分别给了期限；论坛与促销页是个人转述。", kind="spec_value")
S("web-8045", "arenacapacity", "云梯体育馆",
  "云梯体育馆举办演唱会时最多能容纳多少观众？",
  ("https://www.yunti-arena.cn/about/capacity", "场馆概况 | 云梯体育馆", "座席与容量数据。",
   "# 场馆概况\n\n2026 年 6 月改造完成后：固定座席 18600 个；演唱会模式（含内场加座）最大容量 21500 人。\n", "2026-07-05"),
  [("https://baike.example-wiki.cn/yunti", "云梯体育馆 - 百科", "可容纳 2 万人。",
    "# 云梯体育馆\n\n建成于 2009 年，演唱会模式可容纳约 20000 人。（改造前数据）\n", "2025-01-15"),
   ("https://www.yule-bagua.cn/n/yunti-concert", "云梯演唱会门票开售", "场馆 1.8 万座。",
    "# 云梯演唱会门票开售\n\n场馆 1.8 万座，开票即抢空。\n", "2026-08-01")],
  r"最大容量 (\d+) 人", "21500", ["21500", "21,500", "2.15 万", "2.15万"], ["20000", "2 万人", "2万人", "1.8 万", "1.8万", "18000"],
  "演唱会模式最多容纳 21500 人（固定座席 18600 个），依据是云梯体育馆官网 2026 年 6 月改造后的场馆概况；百科是改造前的数据。",
  "官网概况更新于改造完成后，区分了固定座席与演唱会模式；百科和娱乐新闻用的是旧数或座席数。", kind="spec_value")
S("web-8046", "fundcap", "滨江",
  "滨江市住房公积金每月缴存基数上限现在是多少元？",
  ("https://gjj.binjiang.gov.cn/notice/2026-base", "关于调整 2026 年度住房公积金缴存基数的通知", "缴存基数上下限。",
   "# 关于调整 2026 年度住房公积金缴存基数的通知\n\n2026 年 7 月 1 日起至 2027 年 6 月 30 日：月缴存基数上限 31200 元，下限 2690 元。\n", "2026-06-20"),
  [("https://www.caijing-baodian.cn/a/gjj-binjiang", "滨江公积金基数又涨了？", "缴存基数上限 28500 元。",
    "# 滨江公积金基数\n\n按去年的通知，滨江市公积金月缴存基数上限为 28500 元，下限 2490 元。\n", "2026-02-11")],
  r"上限 (\d+) 元", "31200", ["31200", "31,200", "3.12 万", "3.12万"], ["28500", "28,500"],
  "月缴存基数上限现为 31200 元（下限 2690 元），依据是滨江市公积金中心 2026 年度调整通知，7 月 1 日起执行；财经号引用的是上一年度数值。",
  "政府通知给出 2026-07-01 起的新基数，财经号引用的是上一年度通知。", kind="policy_value", sec_first=False)
S("web-8047", "editorversion", "Pinecone",
  "Pinecone 编辑器现在的最新稳定版是多少？",
  ("https://pinecone-editor.org/download/changelog", "Pinecone 更新日志", "Pinecone 编辑器各版本更新记录。",
   "# Pinecone 更新日志\n\n## 2.9.0（稳定版，2026-09-24）\n- 新增多光标列选择\n\n## 2.9.0-beta.2（预览，2026-09-09）\n\n## 2.8.4（稳定版，2026-08-12）\n- 修复大文件卡顿\n", "2026-09-24"),
  [("https://www.rjkuaibao.cn/pinecone-2-8", "Pinecone 2.8 体验", "最新稳定版 2.7.1。",
    "# Pinecone 2.8 体验\n\n本文写于 8 月，当前最新稳定版 2.7.1，运行很稳。\n", "2026-08-15")],
  r"## (\d+\.\d+\.\d+)（稳定版，2026-09-24）", "2.9.0", ["2.9.0"], ["2.7.1"],
  "最新稳定版是 2.9.0（2026-09-24 发布），依据是 Pinecone 官网更新日志；资讯文章写于更早的时候。",
  "官方更新日志有更新的稳定版；资讯文章写于 8 月。", kind="latest_version")
# ---- web en
S("web-8048", "lighthouse", "Kestrel Point",
  "What time is the last guided tour at Kestrel Point Lighthouse on weekends?",
  ("https://www.kestrelpoint.org/visit/tours", "Tours and opening hours | Kestrel Point Lighthouse", "Guided tour times and tickets.",
   "# Tours and opening hours\n\nUpdated 2026-09-01.\n\nGuided tours run every hour on the hour. From 1 September the last tour on Saturdays and Sundays is at 15:00 (winter timetable); weekday last tour is 14:00.\n", "2026-09-01"),
  [("https://www.coastwalkers.example.net/kestrel-point", "Kestrel Point: tips for a day trip", "Weekend last tour is 17:00.",
    "# Kestrel Point day trip\n\nWe went in July: the last tour on weekends is 17:00, so you can easily fit it in after lunch.\n", "2026-07-22")],
  r"Sundays is at (\d+:\d+)", "15:00", ["15:00", "3 pm", "3pm", "3 p.m.", "3:00 pm", "3:00 PM", "3 PM"], ["17:00", "5 pm", "5pm", "5 p.m.", "5 PM"],
  "The last weekend tour is at 15:00 (3 pm) on the winter timetable that started on 1 September, according to the lighthouse's own tours page. A July travel post describes the summer schedule.",
  "The official tours page was updated on 1 September for the winter timetable; the travel post describes the July summer schedule.", kind="opening_hours")
S("web-8049", "carryon", "Corvid Air",
  "What is the carry-on weight limit for Corvid Air economy tickets?",
  ("https://www.corvid.air/help/baggage", "Baggage allowance | Corvid Air", "Cabin and checked baggage rules.",
   "# Baggage allowance\n\nEffective 2026-08-01. Economy: one cabin bag up to 10 kg (55 x 40 x 20 cm) plus one personal item. Checked bags are charged separately.\n", "2026-07-25"),
  [("https://www.budgettravellerforum.example.com/t/corvid-carryon", "Corvid Air carry-on limit?", "It's 7 kg, they weigh at the gate.",
    "# Corvid Air carry-on limit?\n\nIt's 7 kg and they do weigh at the gate, got stung last year.\n", "2025-09-03"),
   ("https://www.wikitravel.example.org/Corvid_Air", "Corvid Air", "Carry-on allowance 8 kg.",
    "# Corvid Air\n\nBaggage: carry-on up to 8 kg.\n", "2025-02-10")],
  r"up to (\d+) kg \(55", "10", ["10 kg", "10kg", "10 kilograms", "10 kilos", "ten kilograms"], ["7 kg", "7kg", "8 kg", "8kg"],
  "Economy passengers can bring one cabin bag up to 10 kg (55 x 40 x 20 cm), per Corvid Air's baggage page effective 1 August 2026. Older forum and wiki entries quote lower limits.",
  "The airline's own baggage page is dated and effective 2026-08-01; the forum and wiki entries are from 2025.", kind="policy_value")
S("web-8050", "ferrybike", "Harbourline",
  "How much does it cost to take a bicycle on the Harbourline ferry?",
  ("https://www.harbourline.example/fares/bicycles", "Bicycle fares | Harbourline Ferries", "Fares for bicycles and e-bikes.",
   "# Bicycle fares\n\nFrom 1 October 2026: bicycles travel for GBP 4.50 each way; e-bikes and cargo bikes GBP 6.00 each way. Folding bikes in a bag travel free.\n", "2026-09-18"),
  [("https://www.cyclingnotes.example.org/harbourline", "Cycling to the island", "Bikes cost GBP 3 on the ferry.",
    "# Cycling to the island\n\nThe Harbourline ferry takes bikes for GBP 3 each way, pay on board.\n", "2025-05-09")],
  r"bicycles travel for GBP ([\d.]+) each way", "4.50", ["4.50", "£4.50", "GBP 4.5", "4.5 pounds"], ["GBP 3 ", "£3 ", "GBP 3.", "£3."],
  "A bicycle costs GBP 4.50 each way from 1 October 2026 (e-bikes GBP 6.00; folding bikes in a bag are free), according to Harbourline's fares page. An older cycling blog's fare is out of date.",
  "The ferry operator's fare page announces the October 2026 price; the blog is from 2025.", kind="price_value", sec_first=False)
S("web-8051", "scootrange", "Orbit Ridge",
  "What is the claimed range of the Orbit Ridge S2 electric scooter on one charge?",
  ("https://www.orbitridge.example/s2/specs", "Orbit Ridge S2 specifications", "Official specs for the S2 scooter.",
   "# Orbit Ridge S2 specifications\n\nMotor: 500 W. Battery: 540 Wh. Claimed range: 55 km (rider 75 kg, 20 km/h, flat road). Weight: 19.6 kg.\n", "2026-05-12"),
  [("https://www.ridertests.example.com/orbit-ridge-s2", "Orbit Ridge S2 review", "Range: 40 km claimed.",
    "# Orbit Ridge S2 review\n\nThe pre-release spec sheet claimed 40 km of range; in our test we got 36 km.\n", "2026-03-03")],
  r"Claimed range: (\d+) km", "55", ["55 km", "55km", "55 kilometres", "55 kilometers"], ["40 km", "40km"],
  "The official claimed range is 55 km (75 kg rider, 20 km/h, flat road), from Orbit Ridge's S2 spec page. The review quotes a pre-release sheet.",
  "The manufacturer's spec page is the primary source and postdates the review's pre-release number.", kind="spec_value")
S("web-8052", "parkpermit", "Marlow County",
  "How much is an annual residential parking permit in Marlow County?",
  ("https://www.marlowcounty.example.gov/parking/permits", "Residential parking permits | Marlow County", "Permit types and fees.",
   "# Residential parking permits\n\nFee schedule adopted 14 July 2026, effective 1 September 2026: annual permit USD 96; second vehicle USD 144; visitor book USD 20.\n", "2026-07-14"),
  [("https://www.marlowlocal.example.com/news/permit-fees", "Parking permit fees going up?", "Annual permit is USD 80.",
    "# Parking permit fees\n\nAn annual residential permit currently costs USD 80, the county says; a council vote is expected in the summer.\n", "2026-05-02")],
  r"annual permit USD (\d+)", "96", ["USD 96", "$96", "96 dollars", "96 USD", "US$96"], ["USD 80", "$80", "80 dollars"],
  "An annual residential permit costs USD 96 since 1 September 2026 (second vehicle USD 144), per the county's permit page. The local news piece was written before the council vote.",
  "The county fee schedule is the adopted, dated source; the news item predates the vote.", kind="price_value")
S("web-8053", "applydeadline", "Ashgrove University",
  "When is the application deadline for the Ashgrove University 2027 undergraduate intake?",
  ("https://www.ashgrove.example.edu/admissions/dates", "Key dates | Ashgrove University Admissions", "Application deadlines for 2027 entry.",
   "# Key dates for 2027 entry\n\nUpdated 2026-09-10.\n\n- Applications open: 1 September 2026\n- Main application deadline: 15 January 2027 (extended)\n- Decisions: from 1 March 2027\n", "2026-09-10"),
  [("https://www.unirankhub.example.com/ashgrove-guide", "Ashgrove University admissions guide", "Deadline is 8 January 2027.",
    "# Ashgrove admissions guide\n\nMain deadline for 2027 entry: 8 January 2027. Apply early.\n", "2026-06-25")],
  r"Main application deadline: (\d+ January 2027)", "15 January 2027", ["15 January 2027", "January 15, 2027", "2027-01-15", "15 Jan 2027", "Jan 15, 2027", "15 January"], ["8 January", "January 8", "2027-01-08", "8 Jan "],
  "The main deadline is 15 January 2027 (extended), according to Ashgrove's admissions key-dates page updated on 10 September 2026. The rankings guide still shows the original date.",
  "The university page is dated later and explicitly notes the extension; the guide has the original date.", kind="event_date")
S("web-8054", "lanternfall", "Lanternfall",
  "On which dates does the Lanternfall Festival run this year?",
  ("https://www.lanternfall.example.org/2026", "Lanternfall Festival 2026", "Dates, venues and tickets.",
   "# Lanternfall Festival 2026\n\nNotice (2026-08-30): the festival moves one week later because of the harbour works. New dates: 16-18 October 2026. Venue: Old Dockyard.\n", "2026-08-30"),
  [("https://www.eventsweekly.example.com/lanternfall", "Autumn festivals to book now", "Lanternfall runs 9-11 October.",
    "# Autumn festivals\n\nLanternfall Festival returns 9-11 October at the Old Dockyard.\n", "2026-06-20")],
  r"New dates: ([\d-]+ October 2026)", "16-18 October 2026", ["16-18 October", "16–18 October", "October 16-18", "October 16–18", "16 to 18 October", "Oct 16-18", "16-18 Oct"], ["9-11 October", "9–11 October", "October 9-11", "October 9–11", "9 to 11 October"],
  "It runs 16-18 October 2026 at the Old Dockyard; the organisers moved it a week later on 30 August because of harbour works. The listings site still shows the original dates.",
  "The festival's own notice postdates the listing and states the new dates.", kind="event_date", sec_first=False)
S("web-8055", "notesprice", "Plover Notes",
  "How much does Plover Notes Pro cost per month now?",
  ("https://www.plovernotes.example/pricing", "Pricing | Plover Notes", "Free, Pro and Team plans.",
   "# Pricing\n\nUpdated 2026-09-03.\n\n- Free: USD 0\n- Pro: USD 6 per month (billed monthly) or USD 60 per year\n- Team: USD 11 per user per month\n", "2026-09-03"),
  [("https://www.softwaredeals.example.com/plover-notes-review", "Plover Notes review 2026", "Pro costs USD 4 a month.",
    "# Plover Notes review\n\nPro is only USD 4 a month, which is great value compared with competitors.\n", "2026-01-19")],
  r"Pro: USD (\d+) per month", "6", ["USD 6", "$6 ", "$6/", "$6.", "6 dollars", "6 USD", "US$6"], ["USD 4", "$4", "4 dollars"],
  "Plover Notes Pro is USD 6 per month billed monthly (USD 60 per year), according to the vendor's pricing page updated 3 September 2026. The review's price is outdated.",
  "The vendor pricing page is current and dated; the review is from January.", kind="price_value")
S("web-8056", "espressowarranty", "Brindle",
  "How long is the manufacturer warranty on the Brindle Q1 espresso machine?",
  ("https://www.brindle.example/support/q1-warranty", "Brindle Q1 warranty", "Warranty terms for the Q1.",
   "# Brindle Q1 warranty\n\nPurchases made on or after 1 June 2026 carry a 3-year manufacturer warranty on the machine and boiler; accessories 1 year.\n", "2026-06-01"),
  [("https://www.coffeegeekz.example.com/brindle-q1", "Brindle Q1 first look", "Comes with a 1-year warranty.",
    "# Brindle Q1 first look\n\nThe Q1 ships with a 1-year warranty, which is on the short side.\n", "2026-02-14")],
  r"carry a (\d)-year manufacturer warranty", "3", ["3-year", "3 year", "three-year", "three year", "3 years", "three years", "Three-year", "Three year", "Three years"], ["1-year warranty", "1 year warranty", "one-year warranty", "one year warranty"],
  "The machine and boiler carry a 3-year manufacturer warranty for purchases from 1 June 2026 (accessories 1 year), per Brindle's support page. The early review's 1-year figure predates the change.",
  "The support page states the warranty by purchase date; the early review predates it.", kind="spec_value", sec_first=False)
S("web-8057", "railyouth", "Northmoor Rail",
  "Up to what age can someone buy a Northmoor Rail youth pass?",
  ("https://www.northmoorrail.example/passes/youth", "Youth Pass | Northmoor Rail", "Eligibility and prices for the Youth Pass.",
   "# Youth Pass\n\nFrom 1 January 2026 the Youth Pass is available to anyone aged 16 to 27 (inclusive). Proof of age required.\n", "2025-12-12"),
  [("https://www.railforum.example.net/t/northmoor-youth", "Northmoor youth pass age limit?", "Under 26s only.",
    "# Northmoor youth pass\n\nIt's for under 26s only, I was refused at 26 years old.\n", "2024-10-30"),
   ("https://www.studentsavings.example.com/rail", "Student rail discounts", "Youth pass up to age 25.",
    "# Student rail discounts\n\nNorthmoor Rail Youth Pass: ages 16 to 25.\n", "2025-04-04")],
  r"aged 16 to (\d+)", "27", ["27 years", "age 27", "aged 27", "16 to 27", "16-27", "16–27", "up to 27", "27 inclusive", "27 or younger", "27 and under", "27th birthday"], ["under 26", "age 25", "ages 16 to 25", "up to 25", "to 26"],
  "The Youth Pass is open to people aged 16 to 27 inclusive since 1 January 2026, per Northmoor Rail's Youth Pass page. Older forum and savings-site pages cite lower age limits.",
  "The operator's page records the age band change effective 2026-01-01.", kind="policy_value", maxc=500)
S("web-8058", "ltsline", "Quillmark",
  "Which Quillmark release is the current LTS?",
  ("https://quillmark.example/releases", "Quillmark releases", "Release channels and support windows.",
   "# Quillmark releases\n\nUpdated 2026-09-15.\n\n| Version | Channel | Release date |\n|---|---|---|\n| 6.1 | Current | 2026-09-08 |\n| 6.0 | LTS | 2026-04-14 |\n| 5.4 | Maintenance | 2025-10-02 |\n", "2026-09-15"),
  [("https://www.devdigest.example.com/quillmark-5-lts", "Quillmark 5 LTS: why upgrade?", "Quillmark 5.4 is the LTS line.",
    "# Quillmark 5 LTS\n\nQuillmark 5.4 is the LTS line, so stick with it for production.\n", "2025-11-03")],
  r"\| (\d\.\d) \| LTS \|", "6.0", ["Quillmark 6.0", "6.0 is the LTS", "6.0 LTS", "version 6.0", "6.0 (LTS)", "6.0"], ["5.4 is the LTS", "Quillmark 5.4 is the", "5.4 LTS"],
  "The current LTS is Quillmark 6.0 (released 2026-04-14), per the official releases page; 5.4 is now only in maintenance, and an older digest article still calls it the LTS line.",
  "The official releases table lists the LTS channel directly and is newer than the article.", kind="latest_version", maxc=500)
S("web-8059", "minpython", "Ferrule",
  "What is the minimum Python version supported by Ferrule 4.0?",
  ("https://ferrule.example/docs/install", "Installation | Ferrule 4.0 docs", "Requirements and install steps.",
   "# Installation (Ferrule 4.0)\n\nLast updated 2026-08-19.\n\nFerrule 4.0 requires Python 3.10 or newer. Support for Python 3.8 and 3.9 was dropped in 4.0.\n", "2026-08-19"),
  [("https://www.pyweekly.example.com/ferrule-3", "Getting started with Ferrule", "Works on Python 3.8+.",
    "# Getting started with Ferrule\n\nFerrule works on Python 3.8 and up, so any recent system Python will do.\n", "2025-06-30")],
  r"requires Python ([\d.]+) or newer", "3.10", ["3.10", "Python 3.10"], ["3.8 and up", "3.8+", "Python 3.8 or", "3.8 or newer", "3.8 and above"],
  "Ferrule 4.0 needs Python 3.10 or newer; 3.8 and 3.9 were dropped in 4.0 according to the official install docs. An older tutorial still lists older Pythons.",
  "The 4.0 install doc is explicit; the tutorial describes the 3.x series.", kind="spec_value", sec_first=False)
S("web-8060", "gantryport", "Gantry",
  "What port does the Gantry dashboard listen on by default in version 2?",
  ("https://gantry.example/docs/v2/config", "Configuration | Gantry v2", "Dashboard and API settings.",
   "# Configuration (v2)\n\nUpdated 2026-07-02.\n\n`dashboard.port` defaults to 7430. v2 moved it from the v1 default to avoid clashes with other local services.\n", "2026-07-02"),
  [("https://stackhelp.example.dev/q/gantry-dashboard-port", "Gantry dashboard port?", "Default is 8080.",
    "# Gantry dashboard port?\n\nAnswer: the dashboard is on http://localhost:8080 by default.\n", "2025-02-20")],
  r"defaults to (\d+)\.", "7430", ["7430"], ["8080"],
  "In Gantry v2 the dashboard listens on port 7430 by default, per the official v2 configuration docs. The v1 default was different.",
  "The v2 configuration page states the new default and the old one explicitly.", kind="lookup_value")
S("web-8061", "maxconn", "Sorrel",
  "What's Sorrel's default max_connections setting in the 3.x series?",
  ("https://sorrel-db.example/docs/3.x/settings", "Settings reference | Sorrel 3.x", "All server settings and defaults.",
   "# Settings reference (3.x)\n\nUpdated 2026-08-08.\n\n`max_connections` — default 400. Raised from 100 in 3.0; each connection uses roughly 6 MB.\n", "2026-08-08"),
  [("https://dbtips.example.net/sorrel-tuning", "Tuning Sorrel", "Default max_connections is 100.",
    "# Tuning Sorrel\n\nBy default max_connections is 100; raise it if you see connection refused errors.\n", "2025-01-11")],
  r"default (\d+)\. Raised", "400", ["defaults to 400", "default of 400", "is 400", "400 connections", "400 by default", "default 400", "= 400", "to 400"], ["is 100", "default 100", "default is 100", "100 connections", "defaults to 100"],
  "In Sorrel 3.x max_connections defaults to 400 (raised from 100 in 3.0), per the official settings reference; older tuning tips still quote 100.",
  "The 3.x reference documents the changed default.", kind="lookup_value")
S("web-8062", "ratelimit", "Wicket",
  "What is the default API rate limit for Wicket's free tier?",
  ("https://wicket.example/docs/api/limits", "Rate limits | Wicket API", "Request limits per plan.",
   "# Rate limits\n\nUpdated 2026-09-12. Free tier: 60 requests per minute. Pro: 600 requests per minute. Limits changed on 1 September 2026; the free tier was previously 30 requests per minute.\n", "2026-09-12"),
  [("https://integrationguide.example.com/wicket", "Wicket integration guide", "Free tier allows 100 requests per minute.",
    "# Wicket integration guide\n\nThe free tier allows 100 requests per minute and Pro 1000.\n", "2026-03-17")],
  r"Free tier: (\d+) requests", "60", ["60 requests", "60 req", "60 calls", "60 per minute", "60/min"], ["100 requests", "1000 requests"],
  "The free tier is limited to 60 requests per minute since the 1 September 2026 change (it was 30 before), according to Wicket's rate-limit docs; the integration guide's 100 is wrong or outdated.",
  "The official limits page is dated 2026-09-12 and lists the current tiers.", kind="lookup_value", sec_first=False)
S("web-8063", "gorgeentry", "Hollin Gorge",
  "How much is the entry fee for an adult at Hollin Gorge nature reserve?",
  ("https://www.hollingorge.example.org/visit/fees", "Fees | Hollin Gorge Nature Reserve", "Entry fees and parking.",
   "# Fees\n\nFrom 1 April 2026: adult entry GBP 7.50, child (5-15) GBP 3.50, under-5s free. Parking GBP 4 for the day.\n", "2026-03-20"),
  [("https://www.walkingholidays.example.com/hollin-gorge", "Hollin Gorge walk guide", "Adults GBP 6 to enter.",
    "# Hollin Gorge walk\n\nEntry for adults is GBP 6 and parking is GBP 3.\n", "2025-07-08")],
  r"adult entry GBP ([\d.]+)", "7.50", ["7.50", "7.5 pounds", "GBP 7.5 "], ["GBP 6 ", "£6 ", "GBP 6.", "£6."],
  "Adult entry is GBP 7.50 from 1 April 2026 (children 5-15 GBP 3.50), per the reserve's fees page; a 2025 walking guide lists a lower fee.",
  "The reserve's fees page gives the April 2026 prices; the guide is from 2025.", kind="price_value")
# ---- hybrid: local record names the object, web gives the current value
S("hyb-8021", "printerwarranty", "Maple",
  "采购清单里那台 Maple 打印机，官方给的整机保修期是多久？",
  ("https://www.maple-print.cn/support/warranty", "保修政策 | Maple 打印机", "各型号整机保修期。",
   "# 保修政策\n\n2026 年 5 月更新。整机保修期：\n\n| 型号 | 整机保修 |\n|---|---|\n| P20 | 18 个月 |\n| P40 | 24 个月 |\n| P60 | 36 个月 |\n", "2026-05-06"),
  [("https://www.dayin-luntan.cn/t/maple-p40", "Maple P40 值不值得买", "P40 保修一年。",
    "# Maple P40 值不值得买\n\n买了 P40，保修一年，墨盒另算。\n", "2026-01-20")],
  r"\| P40 \| (\d+) 个月", "24", ["24 个月", "24个月", "两年", "2 年", "2年"], ["12 个月", "12个月", "保修一年", "保修 1 年"],
  "采购清单里的是 Maple P40（办公室 2 楼），官方保修政策页写 P40 整机保修 24 个月，也就是两年；论坛帖的说法不是官方口径。",
  "清单决定型号 P40，官方保修表按型号给期限；论坛帖未区分型号。",
  files={"采购/设备清单.txt": "打印机：Maple P40（2 楼办公区，2026-03-12 购入）\n投影仪：Vista H3（会议室）\n碎纸机：Gird S8（行政部）\n"},
  vcode='f = files["采购/设备清单.txt"]\nk = re.match(r"打印机：Maple (P\\d+)", f).group(1)\nval = re.search(r"\\| %s \\| (\\d+) 个月" % k, off).group(1)', kind="spec_value")
S("hyb-8022", "gatewayver", "Heron",
  "部署笔记里记的是我们现在跑的 Heron 网关版本，官方最新稳定版是多少？比我们的新吗？",
  ("https://heron-gw.org/releases", "Heron 发布记录", "Heron 网关各版本。",
   "# Heron 发布记录\n\n| 版本 | 通道 | 日期 |\n|---|---|---|\n| 3.7.0-rc.1 | 预览 | 2026-09-20 |\n| 3.6.2 | stable | 2026-09-11 |\n| 3.6.1 | stable | 2026-08-03 |\n| 3.4.1 | stable | 2026-03-09 |\n", "2026-09-20"),
  [("https://www.yunwei-note.cn/heron-3-5", "Heron 3.5 升级记", "目前最新稳定版 3.5.0。",
    "# Heron 3.5 升级记\n\n6 月份我们升到了 3.5.0，也是当时的最新稳定版。\n", "2026-06-18")],
  r"\| (\d+\.\d+\.\d+) \| stable \| 2026-09-11", "3.6.2", ["3.6.2"], ["3.5.0"],
  "我们现在跑的是 3.4.1；官方发布记录里最新稳定版是 3.6.2（2026-09-11 发布），比现在的版本新。3.7.0-rc.1 是预览版，不算。",
  "本地笔记给出当前版本，官方发布表给出最新稳定版；运维博客停在 6 月的 3.5.0，预览版 rc 不是稳定版。",
  files={"运维/部署笔记.md": "生产网关：Heron 3.4.1（2026-03 上线）\n配置目录：/etc/heron\n下次变更窗口：10 月\n"},
  vcode='f = files["运维/部署笔记.md"]\ncur = re.match(r"生产网关：Heron (\\d+\\.\\d+\\.\\d+)", f).group(1)\nstable = re.findall(r"\\| (\\d+\\.\\d+\\.\\d+) \\| stable \\|", off)\nassert cur in stable and cur != stable[0]\nval = stable[0]', kind="latest_version")
S("hyb-8023", "cabinbaggage", "瀚海航空",
  "出差计划里订的是瀚海航空，舱位按计划里写的，官方说这个舱位能免费托运多少公斤？",
  ("https://www.hanhai-air.cn/baggage", "行李额 | 瀚海航空", "各舱位免费托运行李额。",
   "# 行李额\n\n2026 年 9 月起：\n\n| 舱位 | 国内免费托运 |\n|---|---|\n| 经济舱 | 20 公斤 |\n| 超级经济舱 | 25 公斤 |\n| 公务舱 | 40 公斤 |\n", "2026-08-28"),
  [("https://www.chuchai-bang.cn/hanhai", "瀚海航空公务舱体验", "公务舱托运 30 公斤。",
    "# 瀚海航空公务舱体验\n\n公务舱可免费托运 30 公斤，餐食不错。\n", "2025-10-10")],
  r"\| 公务舱 \| (\d+) 公斤", "40", ["40 公斤", "40公斤", "40 kg", "40kg", "40 千克"], ["30 公斤", "30公斤", "30 kg", "30kg"],
  "出差计划里订的是公务舱，官方行李额表写公务舱国内免费托运 40 公斤；体验帖是 2025 年的旧口径。",
  "计划决定舱位=公务舱；官方表按舱位列额度，体验帖写于 2025 年。",
  files={"出差/计划.txt": "舱位：公务舱\n航司：瀚海航空 HH2381\n10 月 14 日 上海—成都\n同行：2 人\n"},
  vcode='f = files["出差/计划.txt"]\ncab = re.match(r"舱位：(\\S+)", f).group(1)\nval = re.search(r"\\| %s \\| (\\d+) 公斤" % cab, off).group(1)', kind="policy_value")
S("hyb-8024", "hallcapacity", "星桥会展中心",
  "租赁合同里订的是星桥会展中心的哪个厅？官网上这个厅剧院式摆放最多能坐多少人？",
  ("https://www.xingqiao-expo.cn/halls", "场地一览 | 星桥会展中心", "各厅面积与容量。",
   "# 场地一览\n\n更新于 2026-08-01。\n\n| 厅 | 面积 | 剧院式容量 | 课桌式容量 |\n|---|---|---|---|\n| A 厅 | 900 ㎡ | 800 人 | 480 人 |\n| B 厅 | 600 ㎡ | 520 人 | 300 人 |\n| C 厅 | 300 ㎡ | 240 人 | 150 人 |\n", "2026-08-01"),
  [("https://www.huiwu-info.cn/xingqiao", "星桥会展中心场地介绍", "B 厅剧院式可容纳 450 人。",
    "# 星桥会展中心场地介绍\n\nB 厅 600 平，剧院式约 450 人，课桌式 280 人。（2024 年资料）\n", "2024-12-05")],
  r"\| B 厅 \| 600 ㎡ \| (\d+) 人", "520", ["520 人", "520人", "520 个座位", "520 座"], ["450 人", "450人"],
  "合同订的是 B 厅；官网场地一览写 B 厅剧院式摆放最多 520 人（课桌式 300 人）。会务网站是 2024 年的旧资料。",
  "合同决定厅号；官网表按厅列容量且更新于 2026-08，会务站资料是 2024 年的。",
  files={"合同/场地租赁.txt": "场地：星桥会展中心 B 厅\n日期：2026-11-20\n用途：年度客户大会\n租金：38000 元\n"},
  vcode='f = files["合同/场地租赁.txt"]\nh = re.match(r"场地：星桥会展中心 (\\w) 厅", f).group(1)\nval = re.search(r"\\| %s 厅 \\| \\d+ ㎡ \\| (\\d+) 人" % h, off).group(1)', kind="spec_value")
S("hyb-8025", "gastier", "安澜燃气",
  "账单备忘里写了我家的用气档次，按安澜燃气官网现行价格，这个档次的气价是多少元每立方米？",
  ("https://www.anlan-gas.cn/price/residential", "居民用气价格 | 安澜燃气", "居民阶梯气价。",
   "# 居民用气价格\n\n2026 年 10 月 1 日起执行：\n\n- 第一档（年用气量 0—300 立方米）：3.15 元/立方米\n- 第二档（301—500 立方米）：3.78 元/立方米\n- 第三档（500 立方米以上）：4.73 元/立方米\n", "2026-09-22"),
  [("https://www.shenghuo-pai.cn/gas-price", "安澜燃气气价一览", "第二档 3.45 元/立方米。",
    "# 安澜燃气气价\n\n第一档 2.88 元，第二档 3.45 元，第三档 4.32 元（2025 年）。\n", "2025-09-30")],
  r"第二档（301—500 立方米）：([\d.]+) 元", "3.78", ["3.78 元", "3.78元", "3.78 块"], ["3.45 元", "3.45元", "3.45 块"],
  "备忘里写的是第二档用气；安澜燃气官网 10 月 1 日起执行的价格里第二档是 3.78 元/立方米。生活号上的是 2025 年旧价。",
  "备忘决定档次=第二档；官网现行价按档给出，旧价来自 2025 年。",
  files={"家庭/账单备忘.txt": "燃气：安澜燃气，今年已用 342 立方米，属于第二档\n水费：按季度缴\n"},
  vcode='f = files["家庭/账单备忘.txt"]\ntier = re.match(r"燃气：.*属于(第.档)", f).group(1)\nval = re.search(r"- %s（[^）]*）：([\\d.]+) 元" % tier, off).group(1)', kind="price_value")
S("hyb-8026", "codingclass", "青禾少儿编程",
  "报名记录里孩子报的是青禾少儿编程的哪个班？官网上这个班一节课多少钱？",
  ("https://www.qinghe-code.cn/courses/fees", "课程与收费 | 青禾少儿编程", "各班型课时费。",
   "# 课程与收费\n\n2026 秋季学期起：\n\n| 班型 | 单节课时费 |\n|---|---|\n| 启蒙班 | 98 元 |\n| 初级班 | 128 元 |\n| 中级班 | 168 元 |\n| 竞赛班 | 228 元 |\n", "2026-08-15"),
  [("https://www.jiaoyu-quan.cn/qinghe", "青禾少儿编程家长测评", "中级班 150 元一节。",
    "# 青禾少儿编程测评\n\n我们报的中级班，150 元一节，老师不错。\n", "2026-01-28")],
  r"\| 中级班 \| (\d+) 元", "168", ["168 元", "168元", "168 块"], ["150 元", "150元", "150 块"],
  "孩子报的是中级班，官网 2026 秋季学期起的收费表里中级班每节 168 元；家长测评写的是春季学期的价格。",
  "报名记录决定班型；官网收费表按班型给价并带学期，测评写于 1 月。",
  files={"家庭/报名记录.txt": "班型：中级班\n孩子：小宇\n机构：青禾少儿编程\n时间：周六 10:00\n"},
  vcode='f = files["家庭/报名记录.txt"]\nk = re.match(r"班型：(\\S+)", f).group(1)\nval = re.search(r"\\| %s \\| (\\d+) 元" % k, off).group(1)', kind="price_value")
S("hyb-8027", "pinlatest", "Tessel",
  "Our requirements.txt pins Tessel. What's the newest stable Tessel 2.x release, and is our pin behind it?",
  ("https://tessel.example/changelog", "Tessel changelog", "Release notes for Tessel.",
   "# Tessel changelog\n\n## 2.6.0 (2026-09-17)\n- Stable. Adds async pools.\n\n## 3.0.0a1 (2026-09-01)\n- Alpha, not for production.\n\n## 2.5.2 (2026-07-30)\n- Stable. Security fix.\n\n## 2.3.1 (2026-02-04)\n- Stable.\n", "2026-09-17"),
  [("https://www.pythonpulse.example.com/tessel-2-5", "What's new in Tessel 2.5", "Latest Tessel 2.x is 2.5.2.",
    "# What's new in Tessel 2.5\n\nAs of August the newest stable Tessel 2.x release is 2.5.2.\n", "2026-08-12")],
  r"## (2\.\d+\.\d+) \(2026-09-17\)", "2.6.0", ["2.6.0"], ["2.5.2 is the", "newest stable is 2.5.2", "latest stable is 2.5.2"],
  "The newest stable 2.x release is Tessel 2.6.0 (2026-09-17), per the official changelog. Our requirements.txt pins 2.3.1, so it is behind (including the 2.5.2 security fix).",
  "The changelog is the primary source and lists 2.6.0; the news post is from August and the 3.0.0a1 alpha is not stable.",
  files={"requirements.txt": "tessel==2.3.1\nrequests==2.32.3\npytest==8.3.2\n"},
  vcode='f = files["requirements.txt"]\ncur = re.match(r"tessel==([\\d.]+)", f).group(1)\nstable = re.findall(r"## (2\\.\\d+\\.\\d+) \\(\\d{4}-\\d\\d-\\d\\d\\)\\n- Stable", off)\nassert cur in stable and cur != stable[0]\nval = stable[0]', kind="latest_version")
S("hyb-8028", "seatprice", "Quartzly",
  "Check docs/vendor-notes.txt for the Quartzly plan we're on and tell me what the vendor currently charges per seat per month for it.",
  ("https://quartzly.example/pricing", "Pricing | Quartzly", "Plans and per-seat pricing.",
   "# Pricing\n\nUpdated 2026-09-08. Per seat, billed monthly:\n\n- Starter: USD 5\n- Business: USD 14\n- Enterprise: contact sales\n\nBusiness was raised on 1 September 2026.\n", "2026-09-08"),
  [("https://www.saascompare.example.com/quartzly", "Quartzly pricing explained", "Business plan is USD 12 per seat.",
    "# Quartzly pricing\n\nStarter USD 5, Business USD 12, Enterprise on request.\n", "2026-04-02")],
  r"Business: USD (\d+)\n", "14", ["USD 14", "$14", "14 dollars", "14 USD", "US$14"], ["USD 12", "$12"],
  "We're on the Business plan, which the vendor's pricing page (updated 2026-09-08) lists at USD 14 per seat per month, up since the end of August. A comparison site still shows the old figure.",
  "The vendor notes name the plan; the vendor's pricing page is current and states the price change date.",
  files={"docs/vendor-notes.txt": "Quartzly: we are on the Business plan, 22 seats, renewed 2026-01.\nBilling contact: finance@\n"},
  vcode='f = files["docs/vendor-notes.txt"]\nplan = re.match(r"Quartzly: we are on the (\\w+) plan", f).group(1)\nval = re.search(r"- %s: USD (\\d+)\\n" % plan, off).group(1)', kind="price_value")
S("hyb-8029", "eoldate", "Mallow",
  "ops/runbook.yaml says which Mallow DB version we run. When does that release series reach end of life according to Mallow?",
  ("https://mallowdb.example/support/lifecycle", "Release lifecycle | Mallow DB", "Support windows per series.",
   "# Release lifecycle\n\nUpdated 2026-08-25.\n\n| Series | End of life |\n|---|---|\n| 9.1 | 2026-11-12 |\n| 9.2 | 2027-05-14 |\n| 9.3 | 2027-11-11 |\n", "2026-08-25"),
  [("https://www.dbaweekly.example.com/mallow-9-2", "Mallow DB 9.2 released", "9.2 is supported until November 2026.",
    "# Mallow DB 9.2 released\n\nAs with 9.1, expect support until November 2026.\n", "2026-02-02")],
  r"\| 9\.2 \| (\d{4}-\d\d-\d\d) \|", "2027-05-14", ["2027-05-14", "14 May 2027", "May 14, 2027", "May 2027", "14 May, 2027"], ["November 2026"],
  "The runbook shows we run Mallow DB 9.2, which reaches end of life on 14 May 2027 per the vendor's lifecycle page. A DBA newsletter's earlier date was for 9.1.",
  "The runbook picks the series; the vendor lifecycle table gives dates per series.",
  files={"ops/runbook.yaml": "version: 9.2.4\nservice: orders-db\nengine: mallow-db\nreplicas: 2\n"},
  vcode='f = files["ops/runbook.yaml"]\nseries = re.match(r"version: (\\d+\\.\\d+)\\.", f).group(1)\nval = re.search(r"\\| %s \\| (\\d{4}-\\d\\d-\\d\\d) \\|" % re.escape(series), off).group(1)', kind="lookup_value")
S("hyb-8030", "railcard", "Fennmoor Rail",
  "Our travel notes say which Fennmoor Rail railcard we're considering. What's the minimum age to buy it according to Fennmoor Rail?",
  ("https://www.fennmoorrail.example/railcards", "Railcards | Fennmoor Rail", "Discount cards and eligibility.",
   "# Railcards\n\nEligibility from 1 March 2026:\n\n- Youth Railcard: ages 16-25\n- Senior Railcard: age 60 or over (lowered in February 2026)\n- Family Railcard: 1-4 adults with 1-4 children\n", "2026-02-20"),
  [("https://www.seniortravel.example.com/fennmoor", "Senior discounts on Fennmoor Rail", "Senior Railcard from age 62.",
    "# Senior discounts\n\nYou need to be 62 or over to buy the Fennmoor Senior Railcard.\n", "2025-11-14")],
  r"Senior Railcard: age (\d+) or over", "60", ["60 or over", "age 60", "aged 60", "60 and over", "60 or older", "60 years", "60+"], ["62 or over", "age 62", "aged 62", "62 and over", "62 or older"],
  "The notes say the Senior Railcard; Fennmoor Rail's railcards page says it is for ages 60 or over from 1 March 2026 (it was higher before). The seniors' travel site is out of date.",
  "Notes name the card; the operator's page records the age threshold change.",
  files={"travel/notes.txt": "Card we're considering: Senior Railcard (for Dad)\nTrip: Leeds to Carlisle, 3 Nov\nFennmoor Rail off-peak singles\n"},
  vcode='f = files["travel/notes.txt"]\ncard = re.match(r"Card we\'re considering: (\\w+) Railcard", f).group(1)\nval = re.search(r"- %s Railcard: age (\\d+) or over" % card, off).group(1)', kind="policy_value")
S("hyb-8031", "hallseats", "Quayside Centre",
  "venue/hire-notes.txt names the hall we shortlisted at the Quayside Centre. How many people does that hall seat in theatre layout, per the venue's own site?",
  ("https://www.quaysidecentre.example/halls", "Halls | Quayside Centre", "Hall sizes and capacities.",
   "# Halls\n\nUpdated 2026-07-11, after the refurbishment.\n\n| Hall | Theatre | Banquet |\n|---|---|---|\n| Cedar Hall | 340 | 220 |\n| Elm Hall | 180 | 120 |\n| Harbour Suite | 90 | 60 |\n", "2026-07-11"),
  [("https://www.eventplanner.example.com/quayside", "Quayside Centre venue profile", "Cedar Hall seats 280 theatre style.",
    "# Quayside Centre\n\nCedar Hall: 280 theatre, 180 banquet (pre-refurbishment figures).\n", "2025-03-21")],
  r"\| Cedar Hall \| (\d+) \|", "340", ["340 people", "340 seats", "340 guests", "340 in theatre", "340 theatre", "340 delegates", "seats 340", "340 (theatre", "capacity of 340", "340 attendees"], ["280 theatre", "280 people", "280 seats", "280 guests"],
  "The notes shortlist Cedar Hall; the venue's own halls page (updated after the refurbishment on 2026-07-11) gives 340 in theatre layout. A directory profile still lists the old 280.",
  "The notes pick the hall; the venue page is newer and post-refurbishment.",
  files={"venue/hire-notes.txt": "Shortlisted at Quayside Centre: Cedar Hall (for the AGM, ~300 delegates). Date 12 Feb 2027.\n"},
  vcode='f = files["venue/hire-notes.txt"]\nhall = re.match(r"Shortlisted at Quayside Centre: (\\w+ \\w+) \\(", f).group(1)\nval = re.search(r"\\| %s \\| (\\d+) \\|" % hall, off).group(1)', kind="spec_value")
S("hyb-8032", "hubrrp", "Alder Hub",
  "shop/stock-note.txt has the Alder Hub model we stock. What is its current recommended retail price according to Alder?",
  ("https://alder.example/hub/pricing", "Alder Hub range and prices", "Official recommended retail prices.",
   "# Alder Hub range\n\nRecommended retail prices from 1 September 2026 (incl. VAT):\n\n| Model | RRP |\n|---|---|\n| Hub Mini | EUR 49 |\n| Hub 2 | EUR 89 |\n| Hub Pro | EUR 149 |\n", "2026-08-30"),
  [("https://www.smarthomereview.example.com/alder-hub-2", "Alder Hub 2 review", "The Hub 2 retails at EUR 79.",
    "# Alder Hub 2 review\n\nAt EUR 79 the Hub 2 undercuts most rivals.\n", "2026-02-09")],
  r"\| Hub 2 \| EUR (\d+) \|", "89", ["EUR 89", "€89", "89 euro", "89 EUR", "89 euros"], ["EUR 79", "€79", "79 euro"],
  "The inventory shows we stock the Alder Hub 2, whose RRP is EUR 89 (incl. VAT) from 1 September 2026 per Alder's price page. The February review's price is the old one.",
  "The CSV names the model; Alder's price page lists RRP by model with an effective date.",
  files={"shop/stock-note.txt": "Stocked model: Alder Hub 2 (14 in stock, SKU AH-02)\nUSB-C cable 1m: 120 in stock\n"},
  vcode='f = files["shop/stock-note.txt"]\nmodel = re.match(r"Stocked model: Alder (Hub \\w+)", f).group(1)\nval = re.search(r"\\| %s \\| EUR (\\d+) \\|" % model, off).group(1)', kind="price_value")

PH = {}
PH["web-8036"] = ["岚城阶梯电价第二档起点", "岚城居民用电 第二档 多少度起", "岚城供电阶梯电价 一档二档分界", "岚城每月用多少度电就进第二档？", "岚城电价阶梯现行标准"]
PH["web-8037"] = ["望潮博物馆周末闭馆时间", "望潮博物馆周六周日几点关门", "去望潮博物馆，周末最晚什么时候能进？几点闭馆", "望潮博物馆开放时间 周末", "望潮博物馆周末下午能逛到几点"]
PH["web-8038"] = ["鹭岛轮渡成人票价", "鹭岛轮渡单程多少钱 大人", "坐鹭岛轮渡一个大人要多少钱", "鹭岛轮渡现行票价 成人 单程", "鹭岛轮渡船票现在什么价"]
PH["web-8039"] = ["云港市图书馆普通图书借期", "云港市图书馆借书能借多久", "云港市图书馆借阅期限 普通图书 几天", "在云港市图书馆借一本书要几天内还", "云港市图书馆借阅规则 借期"]
PH["web-8040"] = ["Lumo X5 电池容量", "Lumo X5 电池多少毫安", "Lumo X5 手机电池 mAh", "Lumo X5 的电池有多大", "Lumo X5 官方参数 电池"]
PH["web-8041"] = ["海燕航空经济舱免费托运行李额", "海燕航空 经济舱 托运行李 多少公斤免费", "坐海燕航空经济舱，托运行李免费多重", "海燕航空国内航线行李额", "海燕航空托运行李规定 经济舱"]
PH["web-8042"] = ["东港国际家居展开幕日期", "东港国际家居展今年什么时候开", "东港国际家居展 2026 几月几号开幕", "东港国际家居展展期", "今年的东港国际家居展哪天开始"]
PH["web-8043"] = ["迅达快递大件附加费起收重量", "迅达快递 单件多重算大件", "迅达快递超过多少公斤要加收附加费", "迅达快递大件规定 公斤", "迅达快递附加费标准"]
PH["web-8044"] = ["Tarn AX6 路由器整机保修", "Tarn AX6 保修几年", "Tarn AX6 官方保修期", "Tarn AX6 路由器保修多少个月", "Tarn AX6 保修政策"]
PH["web-8045"] = ["云梯体育馆演唱会最大容量", "云梯体育馆开演唱会能坐多少人", "云梯体育馆最多容纳观众 演唱会模式", "云梯体育馆容量", "云梯体育馆演唱会能进多少人"]
PH["web-8046"] = ["滨江市住房公积金缴存基数上限", "滨江市公积金月缴存基数最高多少", "滨江市公积金基数上限 2026", "滨江市住房公积金每月最高按多少基数缴", "滨江公积金缴存基数 上限 现行"]
PH["web-8047"] = ["Pinecone 编辑器最新稳定版", "Pinecone 编辑器当前稳定版本号", "Pinecone 最新版本是多少", "Pinecone editor latest stable release", "Pinecone 编辑器更新到哪个版本了"]
PH["web-8048"] = ["Kestrel Point lighthouse last tour weekend", "Kestrel Point Lighthouse weekend tour times", "When does the final guided tour start at Kestrel Point on a Saturday?", "Kestrel Point Lighthouse Sunday last tour", "Kestrel Point lighthouse tours opening hours weekends"]
PH["web-8049"] = ["Corvid Air economy carry-on weight limit", "Corvid Air cabin bag allowance economy", "How heavy can my carry-on be with Corvid Air in economy?", "Corvid Air hand luggage weight", "Corvid Air baggage allowance cabin bag kg"]
PH["web-8050"] = ["Harbourline ferry bicycle fare", "Harbourline ferry cost to bring a bike", "Harbourline bikes on board price each way", "How much is a bike ticket on Harbourline?", "Harbourline ferries bicycle fares"]
PH["web-8051"] = ["Orbit Ridge S2 range", "Orbit Ridge S2 electric scooter claimed range km", "How far can the Orbit Ridge S2 go on a charge according to the maker?", "Orbit Ridge S2 specs range", "Orbit Ridge S2 official range"]
PH["web-8052"] = ["Marlow County residential parking permit fee", "Marlow County annual parking permit cost", "How much is a yearly resident parking permit in Marlow County?", "Marlow County parking permits fees", "Marlow County residential permit price annual"]
PH["web-8053"] = ["Ashgrove University 2027 application deadline", "Ashgrove University undergraduate deadline 2027 entry", "When must I apply to Ashgrove University for 2027?", "Ashgrove University admissions key dates 2027", "Ashgrove University main application deadline"]
PH["web-8054"] = ["Lanternfall Festival 2026 dates", "Lanternfall Festival dates this year", "When is the Lanternfall Festival?", "Lanternfall festival October 2026 dates", "What days does Lanternfall run in 2026?"]
PH["web-8055"] = ["Plover Notes Pro monthly price", "Plover Notes Pro price per month", "How much is Plover Notes Pro a month?", "Plover Notes pricing Pro monthly", "Plover Notes Pro plan cost monthly billing"]
PH["web-8056"] = ["Brindle Q1 espresso machine warranty", "Brindle Q1 warranty length", "How many years of warranty does the Brindle Q1 come with?", "Brindle Q1 manufacturer warranty", "Brindle Q1 espresso warranty period"]
PH["web-8057"] = ["Northmoor Rail youth pass age limit", "Northmoor Rail Youth Pass maximum age", "How old can you be to get the Northmoor Rail youth pass?", "Northmoor Rail Youth Pass eligibility age", "Northmoor Rail youth pass upper age"]
PH["web-8058"] = ["Quillmark LTS version", "Quillmark current LTS release", "Which Quillmark version is the long-term support one?", "Quillmark releases LTS channel", "Quillmark LTS latest"]
PH["web-8059"] = ["Ferrule 4.0 minimum Python version", "Ferrule 4.0 requirements Python", "Which Python do I need for Ferrule 4.0?", "Ferrule 4.0 supported Python versions minimum", "Ferrule 4.0 install requirements"]
PH["web-8060"] = ["Gantry v2 dashboard default port", "Gantry dashboard.port default v2", "Which port does the Gantry v2 dashboard use by default?", "Gantry v2 configuration dashboard port", "Gantry 2 dashboard port default"]
PH["web-8061"] = ["Sorrel 3.x default max_connections", "Sorrel max_connections default value", "How many connections does Sorrel 3 allow by default?", "Sorrel 3.x settings max_connections", "Sorrel database max_connections 3.x default"]
PH["web-8062"] = ["Wicket API free tier rate limit", "Wicket free tier requests per minute", "How many API calls per minute does Wicket allow on the free plan?", "Wicket API rate limits free", "Wicket free plan rate limit default"]
PH["web-8063"] = ["Hollin Gorge nature reserve adult entry fee", "Hollin Gorge adult admission price", "How much does an adult pay to get into Hollin Gorge?", "Hollin Gorge reserve fees adult", "Hollin Gorge nature reserve entry price adult"]

PH["hyb-8021"] = ["设备清单里的打印机，Maple 官网写的整机保修多长？", "我们买的那台 Maple 打印机，官方保修几个月？", "看下采购清单里 Maple 打印机的型号，再查官方保修期", "采购清单上的 Maple 打印机整机保修期是多久（以厂商说法为准）", "Maple 打印机（清单里那台）保修多久"]
PH["hyb-8022"] = ["部署笔记里的 Heron 版本落后官方最新稳定版吗？最新是多少", "Heron 网关最新稳定版是哪个？跟我们生产上的比呢", "查一下 Heron 官方最新 stable，再对照部署笔记里的版本", "我们的 Heron 网关该升级吗？官方现在最新稳定版多少", "Heron 官方最新稳定版本号，对比我们现在跑的"]
PH["hyb-8023"] = ["出差计划里的舱位，瀚海航空官方给多少公斤免费托运？", "我这趟瀚海航空的舱位能免费托运多少公斤", "按计划里订的舱位，查瀚海航空官方行李额", "瀚海航空国内免费托运行李额，我订的那个舱位是多少", "出差订的瀚海航空，托运额度多少公斤（按官网）"]
PH["hyb-8024"] = ["合同里订的是星桥会展中心哪个厅？官网上剧院式容量多少", "星桥会展中心我们租的厅，剧院式最多多少人", "查合同里的厅号，再看星桥会展中心官网的剧院式容量", "租赁合同那个厅，官网写的剧院式摆放容量是多少", "星桥会展中心合同订的厅最多能坐多少人（剧院式）"]
PH["hyb-8025"] = ["我家用气属于哪一档？按安澜燃气官网现价是多少钱一方", "根据账单备忘里的档次，安澜燃气现在多少元每立方米", "安澜燃气官网现行气价，我家那个档次是多少", "账单备忘里写的档次，对应安澜燃气现在的单价", "查备忘里我家的用气档，安澜燃气官网这一档的价格"]
PH["hyb-8026"] = ["孩子报的青禾少儿编程班型，官网一节课多少钱？", "报名记录里的班，青禾官网现在每节多少元", "青禾少儿编程 孩子那个班一节课的价格（看官网）", "看下报名记录报的什么班，再查青禾官网单节课时费", "小宇报的青禾班，官网单节多少钱"]
PH["hyb-8027"] = ["Newest stable Tessel 2.x vs our pin in requirements.txt?", "Is the tessel version pinned in requirements.txt out of date? What is the latest stable 2.x?", "Check Tessel's changelog: what is the newest stable 2.x release and are we behind?", "What stable Tessel 2.x version is current, compared with requirements.txt?", "requirements.txt pins Tessel; what does Tessel's own changelog say is the latest stable 2.x?"]
PH["hyb-8028"] = ["Which Quartzly plan are we on (docs/vendor-notes.txt) and what does it cost per seat today?", "Look at docs/vendor-notes.txt for our Quartzly plan, then get the current per-seat price from Quartzly", "Quartzly: current monthly per-seat price for the plan in our vendor notes", "What's our Quartzly plan's per-seat monthly price right now, per the vendor?", "From docs/vendor-notes.txt find the Quartzly tier, then check Quartzly's pricing page"]
PH["hyb-8029"] = ["When does the Mallow series in ops/runbook.yaml reach end of life?", "ops/runbook.yaml Mallow version: what is the EOL date per Mallow?", "Check the runbook's Mallow DB version, then find its end-of-life date on Mallow's site", "Our Mallow DB version end of life date (see ops/runbook.yaml)", "Mallow lifecycle: EOL for the release series we run in ops/runbook.yaml"]
PH["hyb-8030"] = ["Minimum age for the Fennmoor Rail railcard in our travel notes?", "Which Fennmoor Rail railcard are we considering in the notes, and from what age can it be bought?", "Read the travel notes for the railcard, then check Fennmoor Rail's age requirement", "Fennmoor Rail: age eligibility for the railcard named in travel/notes.txt", "How old do you have to be for the Fennmoor Rail railcard in our trip notes?"]
PH["hyb-8031"] = ["Theatre-layout capacity of the shortlisted Quayside Centre hall in venue/hire-notes.txt", "Look up the shortlisted hall at Quayside Centre and how many it seats theatre style", "venue/hire-notes.txt has the hall; what's its theatre capacity on the Quayside Centre website?", "How many delegates does our shortlisted Quayside Centre hall seat in theatre layout?", "Quayside Centre: theatre seating for the hall in our hire notes"]
PH["hyb-8032"] = ["Alder's current RRP for the hub model in shop/stock-note.txt", "What does Alder say the RRP is for the Hub model we stock (shop/stock-note.txt)?", "Find our Alder Hub model in shop/stock-note.txt and its current recommended price", "Current Alder recommended retail price for the model in our stock note", "Alder Hub model we stock: what is its official RRP now?"]

if __name__ == "__main__":
    ids = [c["cid"] for c in CASES]
    assert len(ids) == 40 and len(set(ids)) == 40
    bad = []
    for c in CASES:
        try:
            build(c)
        except AssertionError as e:
            bad.append(e.args)
    for b in bad:
        print("BAD", b)
    assert not bad
