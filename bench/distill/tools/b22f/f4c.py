"""F4 long multi-turn sessions, cases 34576-34580: a config edited from a web recommendation (3) and long manuals (2)."""
import random

from common import T
from f2 import P, make_pages
from f4 import F4, money
from gen import Gen


def config_text(workers, lines_before, lang):
    rng = random.Random("cfg-%d-%s" % (workers, lang))
    keys = ["log_level: info", "bind: 0.0.0.0", "port: 8443", "tls: true", "timeout_seconds: 30", "retries: 3", "cache_ttl: 600", "metrics: enabled"]
    out = ["# service settings", "service: orders-gateway", "pool:"]
    for i in range(lines_before):
        out.append("  %s_%d: %s" % (rng.choice(["alpha", "beta", "gamma", "delta"]), i, rng.choice(keys).split(": ")[1]))
    out += ["workers: %d" % workers, "queue_depth: 128", "graceful_shutdown: true"]
    return "\n".join(out) + "\n"


def edit_case(cid, lang, *, path, workers, rec, page_spec, p1, p2, p3, p4, url_note=""):
    web = make_pages(cid, [page_spec])
    files = {path: config_text(workers, 55, lang)}
    final = files[path].replace("workers: %d" % workers, "workers: %d" % rec)
    times = rec // workers
    zh = lang == "zh"
    turns = [T(p1, inc=[str(workers)], req=["read_file"]),
             T(p2, inc=[str(rec)], req=["web_fetch"]),
             T(p3, review=None, inc=[]),
             T(p4, inc=[str(rec - workers)], any=["%d 倍" % times, "%d倍" % times, "三倍" if times == 3 else "四倍", "%dx" % times, "%d times" % times,
                                                 "three times" if times == 3 else "four times", "tripled" if times == 3 else "quadrupled"], anytok=False, review="accept")]
    return F4(cid, lang, files, web, turns, rules={path: ["workers: %d" % rec]}, edits=1, calcs=0,
              why="The edit target comes from the web page (turn 2); the last turn compares it with the value read in turn 1: %d -> %d." % (workers, rec),
              steps_text="turn1 read_file/search_text 看 workers；turn2 web_fetch 长页面并跳到推荐值章节；turn3 replace_lines 改成推荐值；turn4 与第一轮的值比较",
              must=("read_file", "web_fetch", "replace_lines"), tt="multi_turn", derived=["workers: %d" % rec, str(rec - workers)])


def spec(lang, url, q, title, topics, intro, lead, rec_fact, rest, date, rec):
    secs = [(h, [t]) for h, t in lead] + [("推荐配置" if lang == "zh" else "Recommended settings", [rec_fact])] + [(h, [t]) for h, t in rest]
    return P(lang, url, q, title, topics, intro, secs, 4400, date, [str(rec)])


def manual(rng, g, lang, title, n_clauses, facts):
    """facts: {clause number: text}; clause lines are one sentence each, blank line between clauses."""
    zh = lang == "zh"
    lines = ["# " + title, ""]
    for n in range(1, n_clauses + 1):
        body = facts.get(n) or g.sentence()
        lines.append(("第 %d 条 " % n if zh else "Clause %d. " % n) + body)
        lines.append("")
    return "\n".join(lines) + "\n"


def manuals_case(cid, lang, docs, topics, p1, p2, p3, p4, out, inc, extra_inc):
    """docs: [(path, title, n_clauses, {clause: fact})]; one fact per turn comes from doc i."""
    rng = random.Random(cid)
    g = Gen(cid, lang, topics)
    files = {path: manual(rng, g, lang, title, n, facts) for path, title, n, facts in docs}
    for path, text in files.items():
        assert 400 <= len(text.split("\n")) <= 1200, (cid, path, len(text.split("\n")))
    turns = [T(p1, inc=[inc[0]], req=["search_text"] if False else []), T(p2, inc=[inc[1]]), T(p3, inc=[inc[2]]), T(p4, inc=[])]
    return F4(cid, lang, files, [], turns, rules={out: list(inc) + list(extra_inc)}, tt="multi_turn", must=("read_file", "write_file", "search_text"),
              why="The final file must carry the fact from turn 1 together with the facts of turns 2 and 3.", edits=1,
              steps_text="turn1-3 各用 search_text 定位条款再 read_file 读几行；turn4 write_file 汇总三条，其中第一条来自第一轮",
              max_calls={"read_file": 12}, never=("web_search", "web_fetch"))


def build():
    edit_case("hyb-34576", "zh", path="部署/订单网关配置.yaml", workers=8, rec=24,
              page_spec=spec("zh", "https://gateway-guide.example/tuning/worker-threads", "网关调优", "订单网关性能调优指南：线程与连接池", ["线程数", "连接池", "队列深度", "超时", "压测"],
                             "网关社区文档 · 2026-10-02", [("为什么要调优", "默认配置面向小流量场景，生产环境通常需要按核数调整。")],
                             "对于 8 核 16 GB 的实例，推荐 workers 设置为 24，连接池大小为 64。", [("压测结果", "在推荐配置下，P99 延迟从 180 毫秒降到 95 毫秒。"), ("注意事项", "workers 超过核数四倍后收益递减。")],
                             "2026-10-02", 24),
              p1="部署文件夹里的订单网关配置，workers 现在设成多少？",
              p2="网关调优指南 https://gateway-guide.example/tuning/worker-threads 里，8 核 16 GB 的实例推荐 workers 设多少？",
              p3="好，把配置里的 workers 改成推荐值。", p4="改完之后，比最开始的值增加了多少？是原来的几倍？")
    edit_case("hyb-34577", "en", path="deploy/billing-worker.yaml", workers=6, rec=18,
              page_spec=spec("en", "https://billingtools.example/docs/scaling-workers", "billing workers", "Scaling billing workers: concurrency guidance", ["workers", "queue depth", "retries", "latency", "load tests"],
                             "Billing platform docs · 2026-09-24", [("Why concurrency matters", "Billing jobs are mostly I/O bound, so adding workers beyond the core count often helps.")],
                             "For a 6 core node the guide recommends workers: 18 with a queue depth of 256.", [("Load test results", "At 18 workers the median job time fell from 410 ms to 190 ms."), ("Caveats", "Above 36 workers the database connection limit becomes the bottleneck.")],
                             "2026-09-24", 18),
              p1="In deploy/billing-worker.yaml, what is workers set to right now?",
              p2="The scaling guide at https://billingtools.example/docs/scaling-workers recommends a value for a 6 core node. What is it?",
              p3="Please change workers in that file to the recommended value.", p4="Compared with what it was originally, by how much did we increase it, and how many times the original value is it now?")
    edit_case("hyb-34578", "zh", path="运维/队列消费者配置.yaml", workers=5, rec=20,
              page_spec=spec("zh", "https://mq-practice.example/consumer-scaling", "消息队列", "消息队列消费者扩容实践", ["消费者", "分区", "积压", "重试", "监控"],
                             "实践文章 · 2026-10-11", [("背景", "业务高峰期消息积压，消费者数量与分区数不匹配是常见原因。")],
                             "当分区数为 20 时，建议把 workers 调到 20，使每个分区有一个独立消费者。", [("效果", "调整后积压清空时间由 40 分钟缩短到 6 分钟。"), ("风险", "workers 大于分区数时多出的消费者会空转。")],
                             "2026-10-11", 20),
              p1="运维文件夹的队列消费者配置里，现在 workers 是几？",
              p2="消息队列扩容的文章在 https://mq-practice.example/consumer-scaling ，分区数是 20 的时候建议 workers 设多少？",
              p3="那就把配置里的 workers 改成文章建议的值。", p4="和最初相比，一共加了多少？是原来的几倍？")
    manuals_case("hyb-34579", "zh",
                 [("制度汇编/员工手册.md", "员工手册", 330, {271: "一线城市出差住宿标准为每晚 650 元，二线城市每晚 480 元，超标准部分个人承担。", 120: "员工试用期为三个月，试用期满经考核合格方可转正。"}),
                  ("制度汇编/费用报销规定.md", "费用报销规定", 340, {288: "单笔金额超过 3000 元的报销须由部门总监审批，超过 20000 元须财务副总裁审批。", 90: "报销单据须在费用发生后 30 日内提交。"}),
                  ("制度汇编/商务接待标准.md", "商务接待标准", 320, {251: "商务接待用餐人均上限为 260 元，需要使用酒类的须提前报备行政部。", 60: "接待须填写事前申请单。"})],
                 ["差旅", "报销", "接待", "住宿", "审批", "票据"],
                 "我第一次出差，先在制度汇编文件夹的员工手册里查一下，一线城市出差住宿每晚的标准是多少？",
                 "费用报销规定里，单笔金额超过 3000 元由谁审批？",
                 "商务接待标准里，用餐人均上限是多少？",
                 "把这三条整理成给新同事的速查，写进 出差速查.md，住宿标准要写上一线城市和二线城市两个数。", "出差速查.md",
                 ["650", "部门总监", "260"], ["480"])
    manuals_case("hyb-34580", "en",
                 [("policies/security-policy.md", "Information security policy", 335, {262: "Production access requires multi-factor authentication and is reviewed every 90 days.", 70: "All laptops must use full-disk encryption."}),
                  ("policies/data-retention-policy.md", "Data retention policy", 340, {283: "Customer support transcripts are deleted 18 months after the ticket is closed.", 110: "Payroll records are kept for seven years."}),
                  ("policies/vendor-policy.md", "Vendor onboarding policy", 330, {257: "A security questionnaire is mandatory for any vendor handling personal data, and renewals happen every 24 months.", 40: "Vendors must be registered in the procurement system."})],
                 ["access", "retention", "vendors", "reviews", "audit", "encryption"],
                 "In the policies folder, how often is production access reviewed according to the security policy?",
                 "And in the data retention policy, when are support transcripts deleted?",
                 "In the vendor onboarding policy, how often are security questionnaires renewed?",
                 "Write a one-page cheat sheet for new managers to cheatsheet-new-managers.md with all three answers; include the access review interval from my very first question.", "cheatsheet-new-managers.md",
                 ["90 days", "18 months", "24 months"], ["multi-factor"])
