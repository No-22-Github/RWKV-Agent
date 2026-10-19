"""Deterministic filler sections for the long web pages (changelog, comments, tables, related links).

Every generator takes a random.Random seeded by the caller, so rebuilding is byte-identical.
"""
from common import est_tokens

ZH_ASPECT = ["启动速度", "内存占用", "同步延迟", "搜索排序", "导出格式", "权限校验", "日志输出", "重试策略", "缓存命中率", "界面响应", "批量导入", "通知合并"]
ZH_PROBLEM = ["偶发卡顿", "显示不全", "重复提示", "数据未刷新", "时区错位", "排序异常", "按钮失效", "进度条不动", "字符乱码", "导出缺列", "连接被意外断开", "草稿丢失"]
ZH_COND = ["网络切换", "窗口缩放", "夜间模式", "离线恢复", "并发操作", "长时间空闲", "文件名含空格", "批量选择", "首次登录", "账号切换", "低电量", "弱网"]
ZH_NAMES = ["林舟", "周小满", "陆远", "韩雪", "吴桐", "Alex", "沈木", "唐小棠", "Kevin", "江临", "何夕", "宋雨", "Mia", "顾北", "钟离"]
ZH_COMMENT = ["写得很清楚，照着做一次就成功了。", "我这边升级之后速度确实快了不少。", "希望能出一个更详细的迁移说明。", "有没有人遇到过同步偶尔失败的情况？",
              "文档里的截图有点旧，界面已经变了。", "用了三个月，整体稳定，就是搜索还可以再快一点。", "感谢更新，期待下个版本的批量功能。",
              "我们团队十几个人都在用，目前没出过大问题。", "客服回复很及时，点赞。", "建议把常见问题单独放到首页。", "这个功能我找了好久，原来在设置里面。"]
EN_ASPECT = ["startup time", "memory use", "sync latency", "search ranking", "export format", "permission checks", "log output", "retry policy", "cache hit rate",
             "UI responsiveness", "bulk import", "notification batching"]
EN_PROBLEM = ["an occasional stall", "a truncated label", "a duplicate prompt", "stale data", "a timezone offset", "a wrong sort order", "a dead button",
              "a frozen progress bar", "garbled characters", "a missing column in exports", "an unexpected disconnect", "a lost draft"]
EN_COND = ["switching networks", "resizing the window", "dark mode", "resuming offline", "concurrent edits", "a long idle period", "file names with spaces",
           "selecting many rows", "first sign-in", "switching accounts", "low battery", "a weak connection"]
EN_NAMES = ["Priya", "Tomasz", "Wen", "Daria", "Marcus", "Ines", "Kofi", "Lena", "Sasha", "Omar", "Hana", "Pavel", "Rosa", "Dmitri", "Nina"]
EN_COMMENT = ["Clear write-up, worked on the first try.", "Noticeably faster after the upgrade on my side.", "Would love a more detailed migration note.",
              "Has anyone seen sync fail now and then?", "The screenshots are a bit old, the UI has changed.", "Three months in and it is stable, search could be quicker.",
              "Thanks for the update, looking forward to the bulk features.", "Our team of a dozen uses it daily without trouble.",
              "Support replied quickly, appreciated.", "Maybe move the FAQ to the front page.", "Took me a while to find this setting, it is under Preferences."]


def changelog(rng, product, modules, lang, n, start=(3, 1)):
    out = []
    major, minor = start
    patch = rng.randint(2, 9)
    month, day = 9, 20
    for _ in range(n):
        m1, m2 = rng.sample(modules, 2)
        if lang == "zh":
            a, p, c = rng.choice(ZH_ASPECT), rng.choice(ZH_PROBLEM), rng.choice(ZH_COND)
            out.append("### %s %d.%d.%d（2026-%02d-%02d）\n- 修复了「%s」在%s时%s的问题\n- 优化了「%s」的%s\n" % (product, major, minor, patch, month, day, m1, c, p, m2, a))
        else:
            a, p, c = rng.choice(EN_ASPECT), rng.choice(EN_PROBLEM), rng.choice(EN_COND)
            out.append("### %s %d.%d.%d (2026-%02d-%02d)\n- Fixed %s in %s when %s\n- Improved %s for %s\n" % (product, major, minor, patch, month, day, p, m1, c, a, m2))
        patch -= 1
        if patch < 0:
            patch = rng.randint(3, 8)
            minor -= 1
        day -= rng.randint(3, 9)
        if day < 1:
            day += 28
            month -= 1
        if month < 1:
            month = 12
    return "\n".join(out)


def comments(rng, lang, n):
    names = ZH_NAMES if lang == "zh" else EN_NAMES
    texts = ZH_COMMENT if lang == "zh" else EN_COMMENT
    out = []
    for _ in range(n):
        if lang == "zh":
            out.append("- **%s**（%d 天前）：%s" % (rng.choice(names), rng.randint(1, 60), rng.choice(texts)))
        else:
            out.append("- **%s** (%d days ago): %s" % (rng.choice(names), rng.randint(1, 60), rng.choice(texts)))
    return "\n".join(out)


def param_table(lang, rows, prefix):
    """rows: list of (name, default, description)."""
    head = "| 参数 | 默认值 | 说明 |\n| --- | --- | --- |\n" if lang == "zh" else "| Option | Default | Notes |\n| --- | --- | --- |\n"
    return head + "\n".join("| `%s.%s` | %s | %s |" % (prefix, r[0], r[1], r[2]) for r in rows) + "\n"


def related(rng, lang, topics, n, domain):
    pick = rng.sample(topics, min(n, len(topics)))
    if lang == "zh":
        return "\n".join("- [%s](https://%s/docs/a%03d)（阅读约 %d 分钟）" % (t, domain, rng.randint(1, 999), rng.randint(2, 12)) for t in pick)
    return "\n".join("- [%s](https://%s/docs/a%03d) (about %d min read)" % (t, domain, rng.randint(1, 999), rng.randint(2, 12)) for t in pick)


def tokens(text):
    return est_tokens(text)
