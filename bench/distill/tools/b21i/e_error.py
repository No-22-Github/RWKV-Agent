"""33047-33056 error_meaning."""
from common import *


def er(cid, brand, pages, p1, inc1, p2=None, inc2=None, any1=None, files=None, pol=None, level="L1", why="", req2=False):
    web = [fx(brand, u, t, s, c, d) for (u, t, d, s, c) in pages]
    turns = [T(p1, req=["web_fetch"], inc=inc1, any=any1 or [])]
    if p2:
        turns.append(T(p2, req=["web_fetch"] if req2 else [], inc=inc2))
    mk(cid, tt="error_meaning", desc="Explain a vendor error message using the vendor's reference page (%s)" % brand, web=web, turns=turns,
       traps=["TR-DECOY"], ref="搜索错误码 -> 打开错误码参考页 -> 说明含义与处理办法", why=why or "Meaning and fix are only on the reference page.",
       trap_notes=["相邻错误码含义不同。"], policy=pol or WSF, level="L2" if p2 else level, ref_calls=4 if p2 else 3, files=files, sub="er")


def build():
    er("web-33047", "Harrow Storage", [
        ("https://harrowstorage.example/docs/errors/E4012", "Error E4012", "2026-08-01", "Error code reference.", "# E4012: bucket quota exceeded\n\nThe bucket has reached its object quota (default 1,000,000). Delete unused objects or request a quota increase from Settings > Limits. Writes fail until usage drops below the quota."),
        ("https://harrowstorage.example/docs/errors/E4013", "Error E4013", "2026-08-01", "Error code reference.", "# E4013: request rate limited\n\nToo many requests per second. Retry with exponential backoff.")],
       "Harrow Storage keeps throwing 'E4012' when I upload. What does it mean and how do I fix it?", ["quota"])
    er("web-33048", "凌霄物流", [
        ("https://lingxiao-express.example/help/status-S207", "状态码 S207 - 凌霄物流", "2026-09-02", "物流状态码说明。", "# S207：待补充收件人信息\n\n快递员无法联系收件人且地址缺少门牌号。请在 App「我的快递」中补充电话或门牌，72 小时内未补充将退回寄件人。"),
        ("https://lingxiao-express.example/help/status-S209", "状态码 S209 - 凌霄物流", "2026-09-02", "物流状态码说明。", "# S209：已签收待确认\n\n包裹已投递至代收点，收件人 48 小时内可到点取件。")],
       "我的快递在凌霄物流显示 S207 是什么意思，要怎么处理？", ["72", "门牌"])
    er("web-33049", "Tessel API", [
        ("https://tessel-api.example/reference/errors", "API error reference - Tessel", "2026-09-10", "Errors returned by the Tessel API.", "# Errors\n\n401 invalid_token: the token expired or was revoked. Create a new token in the dashboard.\n403 scope_missing: the token lacks the required scope; the response lists missing scopes.\n429 slow_down: you exceeded 120 requests per minute.\n422 bad_cursor: the pagination cursor is older than 10 minutes.")],
       "Our Tessel API calls return 422 with 'bad_cursor'. What does that mean?", [], any1=["10 minutes", "10 min", "ten minutes", "10-minute"], p2="OK, and what would a 429 slow_down mean for us - what's the cap?", inc2=["120"])
    er("web-33050", "栖霞支付", [
        ("https://qixia-pay.example/dev/err-code", "错误码对照 - 栖霞支付", "2026-08-19", "栖霞支付开发者错误码。", "# 错误码\n\nQX1001：签名校验失败，检查商户密钥与参数排序。\nQX1004：订单金额与下单时不一致。\nQX1008：商户未开通该支付方式，需在商户后台申请开通，审核 1–3 个工作日。")],
       "接入栖霞支付时返回 QX1008，什么意思？", ["开通"], p2="审核大概要多久？", inc2=["工作日"], why="QX1008 与 QX1004 相邻。")
    er("web-33051", "Mosswood IDE", [
        ("https://mosswood-ide.example/kb/license-error-217", "License error 217", "2026-07-21", "Knowledge base article.", "# License error 217\n\nMeans the license server could not be reached within 10 seconds. Check proxy settings under Preferences > Network, or set MOSSWOOD_LICENSE_OFFLINE=1 to use the 7-day offline grace period.")],
       "Mosswood IDE 在公司启动时弹出 license error 217，这是怎么回事，怎么解决？", ["MOSSWOOD_LICENSE_OFFLINE"])
    er("web-33052", "象山电力", [
        ("https://xiangshan-power.example/faq/meter-e05", "电表故障码 E05 - 象山电力", "2026-06-30", "智能电表故障码说明。", "# 电表显示 E05\n\nE05 表示电池电量低（不是欠费）。电表仍可正常计量，请在 30 天内预约上门换电池，免费。\n\nE03 才表示余额不足。")],
       "家里电表显示 E05，是不是欠费了？象山电力怎么说的？", ["电池"], why="E05 与 E03 易混。")
    er("web-33053", "Paperlane Print", [
        ("https://paperlane-print.example/support/fault-B18", "Printer fault B18", "2026-08-12", "Fault code explained.", "# Fault B18\n\nCarriage jam detected. Power off, open the rear cover and remove any paper scraps from the rail. Do not pull the carriage by hand while powered. If B18 returns after cleaning, the encoder strip needs replacing (part PE-44)."),
        ("https://paperlane-print.example/support/fault-B81", "Printer fault B81", "2026-08-12", "Fault code explained.", "# Fault B81\n\nInk waste pad nearly full. Service required.")],
       "My Paperlane printer shows B18. What does it mean and what should I try first?", ["jam"], p2="It came back after cleaning. What part do I need?", inc2=["PE-44"])
    er("web-33054", "海棠课堂", [
        ("https://haitang-class.example/help/video-error", "视频播放错误 - 海棠课堂", "2026-09-07", "视频无法播放的常见错误码。", "# 视频播放错误\n\n- V-301：网络不稳定，建议切换到 480p 或下载离线课件；\n- V-322：账号在另一台设备同时播放，一个账号最多同时 2 台设备；\n- V-340：课程已过有效期，需续费。")],
       "海棠课堂上课时弹出 V-322，是什么问题？", [], any1=["2 台", "2台", "两台", "两个设备", "2 个设备", "2 devices", "two devices"], why="V-301/322/340 含义各异。")
    er("web-33055", "Cinder Deploy", [
        ("https://cinder-deploy.example/docs/troubleshoot", "Troubleshooting - Cinder Deploy", "2026-09-01", "Common deploy failures.", "# Troubleshooting\n\n`ERR_HEALTHCHECK_TIMEOUT`: the new release did not pass its health check within 90 seconds, so traffic stays on the previous release. Raise `healthcheck.timeout` or fix the /healthz endpoint.\n\n`ERR_IMAGE_PULL`: the registry rejected credentials.")],
       "Cinder Deploy rolled back and says ERR_HEALTHCHECK_TIMEOUT. Did my new version go live?", ["90"], p2="So what setting do I raise?", inc2=["healthcheck.timeout"], why="Traffic stays on the old release.")
    er("web-33056", "鹤鸣打印", [
        ("https://heming-print.example/help/order-fail", "下单失败提示 - 鹤鸣打印", "2026-08-05", "下单失败提示说明。", "# 下单失败提示\n\n「文件分辨率过低」：上传图片低于 150 DPI，成品会模糊，请换更高分辨率原图。\n「出血线缺失」：文件四周需各留 3 mm 出血。")],
       "鹤鸣打印下单时提示“出血线缺失”，是什么意思，该怎么改文件？", [], any1=["3 mm", "3mm", "3 毫米", "3毫米"])
