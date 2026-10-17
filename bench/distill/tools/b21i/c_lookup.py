"""33025-33035 lookup_value."""
from common import *


def lk(cid, brand, pages, p1, val, p2=None, val2=None, trap="TR-DECOY", pol=None, level="L1", why="", fetch=True, files=None):
    """pages: list of (url, title, date, snippet, content)."""
    web = [fx(brand, u, t, s, c, d) for (u, t, d, s, c) in pages]
    def _t(p, v, req=()):
        return T(p, req=req, any=v) if isinstance(v, list) else T(p, req=req, inc=[v])
    turns = [_t(p1, val, ["web_fetch"] if fetch else ["web_search"])]
    if p2:
        turns.append(_t(p2, val2))
    mk(cid, tt="lookup_value", desc="Look up one concrete value for a fictional site (%s)" % brand, web=web, turns=turns, traps=[trap],
       ref="web_search -> " + ("web_fetch 对应页 -> 取值" if fetch else "从摘要取值"), why=why or "Only one page carries the asked value.",
       trap_notes=["旁边有相近数值的页面。"], policy=pol or (WSF if fetch else WS), level="L2" if p2 else level,
       ref_calls=4 if p2 else 2, files=files, sub="lk")


def build():
    lk("web-33025", "Alder Parking", [
        ("https://alderparking.example/rates/downtown", "Downtown garage rates", "2026-09-02", "Hourly and daily rates for the downtown garage.", "# Downtown garage\n\nHourly 4 dollars, daily maximum 28 dollars, evening flat rate 9 dollars after 6 pm."),
        ("https://alderparking.example/rates/airport", "Airport lot rates", "2026-09-02", "Hourly and daily rates for the airport lot.", "# Airport lot\n\nHourly 3 dollars, daily maximum 19 dollars, weekly 95 dollars.")],
       "Alder Parking 市中心车库一天最高收费多少？", "28", p2="And the weekly rate at the airport lot?", val2="95")
    lk("web-33026", "枫桥驾校", [
        ("https://fengqiao-drive.example/fees/c1", "C1 班型收费 - 枫桥驾校", "2026-08-20", "C1 班型学费与补考费。", "# C1 班型\n\n学费 4680 元（含 2 次补考），超出每次补考费 150 元。场地练车每小时 60 元。"),
        ("https://fengqiao-drive.example/fees/c2", "C2 班型收费 - 枫桥驾校", "2026-08-20", "C2 班型学费与补考费。", "# C2 班型\n\n学费 5280 元（含 2 次补考），超出每次补考费 180 元。")],
       "枫桥驾校 C1 班型补考一次要多少钱（超出免费次数以后）？", "150", why="C1 与 C2 页面相似，数值不同。")
    lk("web-33027", "Lumen Telescope Co", [
        ("https://lumen-scopes.example/spec/x9", "X9 spec sheet", "2026-07-30", "X9 aperture 130 mm, weight 4.2 kg.", "# X9\n\nAperture 130 mm, focal length 650 mm, weight 4.2 kg.")],
       "What's the focal length of the Lumen X9 telescope?", "650", trap="TR-SNIPPETVAGUE", why="Focal length only in page body.", level="L1")
    lk("web-33028", "南浦花卉市场", [
        ("https://nanpu-flower.example/info/open", "营业信息 - 南浦花卉市场", "2026-09-05", "南浦花卉市场周末营业时间 7:30-17:00，工作日 7:30-16:00。", "# 营业信息\n\n周一至周五 7:30–16:00，周末 7:30–17:00，每月 1 日闭市盘点。")],
       "南浦花卉市场周末几点关门？", "17:00", p2="那每月几号会闭市？", val2="1", why="摘要即有答案，对照题。", fetch=False, trap="TR-EARLYHIT", level="L0")
    lk("web-33029", "Orchard SDK", [
        ("https://orchard-sdk.example/docs/rate-limits", "Rate limits - Orchard SDK", "2026-09-11", "Default API rate limits by plan.", "# Rate limits\n\nFree: 60 requests per minute. Pro: 600 per minute. Enterprise: custom. Burst allowance is 2x for 10 seconds."),
        ("https://orchard-sdk.example/docs/rate-limits-2025", "Rate limits (2025, archived)", "2025-06-01", "Archived rate limits.", "# Rate limits (archived)\n\nFree: 30 requests per minute. Pro: 300 per minute.")],
       "What's the Pro plan rate limit for Orchard SDK per minute?", "600", why="Archived 2025 page shows 300; current page 600.", trap="TR-WEBSTALE")
    lk("web-33030", "银杏社区医院", [
        ("https://yinxing-clinic.example/dept/pediatrics", "儿科门诊 - 银杏社区医院", "2026-09-01", "儿科门诊时间与挂号方式。", "# 儿科门诊\n\n周二、周四、周六 8:00–11:30。挂号费 8 元，可在微信公众号预约，当天号源 20 个。"),
        ("https://yinxing-clinic.example/dept/dental", "口腔科 - 银杏社区医院", "2026-09-01", "口腔科门诊时间与挂号方式。", "# 口腔科\n\n周一至周五 8:00–16:00。挂号费 15 元。")],
       "银杏社区医院儿科挂号费多少，周几有门诊？", ["8 元", "8元", "8块"], p2="口腔科挂号费呢？", val2=["15 元", "15元", "15块"], why="两个科室挂号费不同。")
    lk("web-33031", "Foxglove Bikes", [
        ("https://foxglovebikes.example/warranty", "Warranty - Foxglove Bikes", "2026-05-12", "Frame, motor and battery warranty terms.", "# Warranty\n\nFrame: 5 years. Motor: 3 years. Battery: 2 years or 500 charge cycles, whichever comes first. Paint is not covered.")],
       "How long is the battery warranty on a Foxglove e-bike?", "500", trap="TR-SNIPPETVAGUE")
    lk("web-33032", "潮汐音乐节", [
        ("https://chaoxi-fest.example/tickets", "购票信息 - 潮汐音乐节", "2026-09-15", "早鸟票已售罄，普通票开售中。", "# 购票信息\n\n早鸟票（已售罄）380 元；普通票 480 元；双日联票 780 元；儿童（1.2 米以下）免票但须有成人陪同。")],
       "潮汐音乐节现在买普通票多少钱？早鸟票还有吗？", "480", why="早鸟价是干扰项。")
    lk("web-33033", "Plover Ledger", [
        ("https://plover-ledger.example/help/export", "Exporting data - Plover Ledger", "2026-08-03", "Supported export formats.", "# Exporting data\n\nExport formats: CSV, XLSX, QIF. The maximum export is 50000 rows per file; larger sets are split automatically."),
        ("https://plover-ledger.example/help/import", "Importing data - Plover Ledger", "2026-08-03", "Supported import formats.", "# Importing data\n\nImport formats: CSV, OFX. The maximum import is 10000 rows per file.")],
       "Plover Ledger 单个文件最多能导出多少行？", ["50000", "50,000", "5 万", "5万"], p2="And what about importing?", val2=["10000", "10,000", "1 万", "1万"], trap="TR-DECOY")
    lk("web-33034", "云岫茶舍", [
        ("https://yunxiu-tea.example/menu/seasonal", "秋季限定 - 云岫茶舍", "2026-09-20", "秋季限定饮品与价格。", "# 秋季限定\n\n桂花乌龙 32 元，栗子奶盖 36 元，烤梨茶 30 元。9 月 23 日起供应至 11 月 15 日。"),
        ("https://yunxiu-tea.example/menu/summer", "夏季限定（已下架）- 云岫茶舍", "2026-06-10", "夏季限定饮品，已下架。", "# 夏季限定（已下架）\n\n荔枝冷萃 28 元，杨梅气泡 30 元。")],
       "云岫茶舍的栗子奶盖现在卖多少钱？", "36", why="夏季页已下架，价格不同。", trap="TR-WEBSTALE")
    lk("web-33035", "Kiln Fonts", [
        ("https://kilnfonts.example/license/web", "Web license - Kiln Fonts", "2026-04-09", "Web font licensing by monthly page views.", "# Web license\n\nUp to 100k page views per month: 49 dollars per year. Up to 1M: 149 dollars per year. Above that, contact sales.")],
       "What does Kiln Fonts charge per year for a web license covering up to 1M monthly page views?", "149", trap="TR-SNIPPETVAGUE")
