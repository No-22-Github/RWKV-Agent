"""Deterministic filler generators for b23g (long, realistic-looking files).

Every generator returns a list of blocks (a block is a list of lines that must stay together);
`compose()` stitches blocks and inserts planted blocks at block boundaries near a target line.
"""
import random

# ---------------------------------------------------------------- helpers


def pick(r, xs):
    return xs[r.randrange(len(xs))]


def compose(blocks, plants, header=(), footer=(), n=400):
    """blocks: list[list[str]] (filler), plants: list[(target_line, [lines])], returns list of lines."""
    out = list(header)
    todo = sorted(plants, key=lambda p: p[0])
    bi = 0
    while True:
        while todo and len(out) >= todo[0][0]:
            out.extend(todo.pop(0)[1])
        if bi >= len(blocks):
            if todo:
                out.extend(todo.pop(0)[1])
                continue
            break
        if len(out) >= n and not todo:
            break
        out.extend(blocks[bi])
        bi += 1
    out.extend(footer)
    return out


def text(lines):
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- english prose docs

EN_SUBJ = ["The on-call engineer", "Each team lead", "The platform group", "A requesting service", "The review board",
           "Every contractor", "The release manager", "A regional office", "The data steward", "The support desk",
           "Any new hire", "The audit team", "The facilities group", "A project sponsor", "The security liaison"]
EN_VERB = ["must record", "should confirm", "is expected to attach", "may request", "shall archive", "needs to update",
           "has to forward", "is asked to review", "can raise", "must not delete", "should summarise", "is required to log"]
EN_OBJ = ["the intake form", "a short status note", "the relevant ticket number", "the signed checklist", "the shared calendar entry",
          "an owner and a backup", "the draft agenda", "the evidence folder", "the vendor reference", "a one-line rationale",
          "the weekly digest", "the access request", "the handover sheet", "the cost centre code", "the site visit record"]
EN_TAIL = ["before the end of the working day.", "within the agreed review window.", "whenever the scope changes.",
           "once the request has been approved.", "and keep the original unchanged.", "unless a manager waives the step.",
           "so that later audits can trace it.", "and notify the others in the group.", "at the start of each cycle.",
           "in the team workspace, not by email.", "and mention any open questions.", "before the next planning meeting."]
EN_HEAD_A = ["Intake", "Review", "Handover", "Archive", "Approval", "Onboarding", "Reporting", "Access", "Capacity", "Scheduling",
             "Procurement", "Training", "Documentation", "Communication", "Retention"]
EN_HEAD_B = ["procedure", "checklist", "responsibilities", "notes", "workflow", "guidelines", "expectations", "rules", "overview", "steps"]
EN_BUL = ["Keep entries short and dated.", "Link to the source instead of copying it.", "Name one owner per action.",
          "Close the loop in the same channel.", "Use the shared template, not a personal one.", "Flag blockers early.",
          "Record decisions, not discussions.", "Check the previous cycle's open items first.", "Ask before reassigning work.",
          "Store attachments in the team folder."]


def en_doc_blocks(r, n_blocks=200, start=1):
    bl = []
    for i in range(n_blocks):
        k = start + i
        b = ["", "## %d.%d %s %s" % (k // 6 + 1, k % 6 + 1, pick(r, EN_HEAD_A), pick(r, EN_HEAD_B)), ""]
        t = r.random()
        if t < 0.6:
            for _ in range(r.randint(2, 4)):
                b.append("%s %s %s %s" % (pick(r, EN_SUBJ), pick(r, EN_VERB), pick(r, EN_OBJ), pick(r, EN_TAIL)))
        elif t < 0.85:
            for x in r.sample(EN_BUL, r.randint(3, 5)):
                b.append("- " + x)
        else:
            b += ["| Step | Owner | Due |", "|---|---|---|"]
            for j in range(r.randint(3, 4)):
                b.append("| %s | %s | day %d |" % (pick(r, EN_HEAD_A).lower(), pick(r, ["lead", "steward", "desk", "sponsor"]), r.randint(1, 9)))
        bl.append(b)
    return bl


# ---------------------------------------------------------------- english changelog

CH_ADD = ["Added a --dry-run flag to the sync command.", "Added pagination to the audit listing.", "Added retry counters to the health page.",
          "Added support for ISO week dates in filters.", "Added a warning when a token is close to expiry.", "Added bulk import for tags.",
          "Added a compact output mode.", "Added keyboard shortcuts to the dashboard.", "Added locale-aware date formatting."]
CH_FIX = ["Fixed a crash when the config directory was empty.", "Fixed duplicate rows after a partial import.", "Fixed wrong sort order on ties.",
          "Fixed a race between flush and shutdown.", "Fixed the progress bar overshooting 100%.", "Fixed missing newline at end of exports.",
          "Fixed an off-by-one in range queries.", "Fixed stale cache after a rename.", "Fixed a typo in the French translation.",
          "Fixed sporadic 404s behind the proxy.", "Fixed memory growth in the long-poll handler."]
CH_CHG = ["Changed the default log level to info.", "Changed export filenames to include the date.", "Changed the minimum supported Node version.",
          "Updated bundled certificates.", "Reworded several error messages.", "Moved the settings page under Account.",
          "Tightened input validation on usernames.", "Switched the build to a faster bundler."]


def changelog_blocks(r, top=(2, 9, 4), special=None, n_blocks=260, month0=(2026, 9)):
    special = special or {}
    ma, mi, pa = top
    y, m = month0
    bl = []
    for i in range(n_blocks):
        ver = "%d.%d.%d" % (ma, mi, pa)
        day = r.randint(2, 27)
        b = ["", "## %s - %04d-%02d-%02d" % (ver, y, m, day), ""]
        pool = CH_ADD + CH_FIX + CH_FIX + CH_CHG
        for x in r.sample(pool, r.randint(2, 4)):
            b.append("- " + x)
        b.extend(special.get(ver, []))
        bl.append(b)
        # step to previous version
        if pa > 0 and r.random() < 0.7:
            pa -= 1
        elif mi > 0:
            mi -= 1
            pa = r.randint(1, 4)
        else:
            ma -= 1
            mi = 9
            pa = r.randint(0, 3)
        m -= 1 if r.random() < 0.6 else 0
        if m == 0:
            m = 12
            y -= 1
    return bl


# ---------------------------------------------------------------- chinese prose docs

ZH_SUBJ = ["各部门负责人", "项目经理", "值班同事", "行政同事", "审核人", "新入职员工", "采购专员", "数据管理员", "安全联络人", "财务助理", "各区域办公室", "合同经办人"]
ZH_VERB = ["需要提前登记", "应当及时确认", "须按模板填写", "可以向上级申请", "必须留存记录", "应在系统中更新", "要同步通知相关人员", "不得擅自删除"]
ZH_OBJ = ["申请单", "进度说明", "对应的工单编号", "签字确认的清单", "共享日历中的安排", "负责人和备份人", "会议议程草稿", "佐证材料", "供应商联系记录", "变更理由"]
ZH_TAIL = ["，并在当天内完成。", "，超过期限需说明原因。", "，范围变化时重新提交。", "，审批通过后方可执行。", "，原件保持不变。", "，特殊情况由主管豁免。", "，便于后续审计追溯。", "，并抄送本组同事。"]
ZH_HEAD_A = ["申请", "审核", "交接", "归档", "审批", "入职", "汇报", "权限", "排期", "采购", "培训", "沟通", "留存"]
ZH_HEAD_B = ["流程", "要求", "职责", "说明", "规范", "注意事项", "步骤"]
ZH_BUL = ["记录要简短并注明日期。", "引用来源，不要整段复制。", "每项事务只指定一位负责人。", "在原渠道内闭环。", "使用统一模板。", "尽早提示阻塞项。", "只记结论，不记过程。", "先核对上一周期遗留事项。", "调整分工前先沟通。", "附件统一放在团队目录。"]


def zh_doc_blocks(r, n_blocks=200, start=1):
    bl = []
    for i in range(n_blocks):
        k = start + i
        b = ["", "## 第%d章第%d节 %s%s" % (k // 6 + 1, k % 6 + 1, pick(r, ZH_HEAD_A), pick(r, ZH_HEAD_B)), ""]
        t = r.random()
        if t < 0.6:
            for _ in range(r.randint(2, 3)):
                b.append("%s%s%s%s" % (pick(r, ZH_SUBJ), pick(r, ZH_VERB), pick(r, ZH_OBJ), pick(r, ZH_TAIL)))
        elif t < 0.85:
            for x in r.sample(ZH_BUL, r.randint(3, 4)):
                b.append("- " + x)
        else:
            b += ["| 环节 | 责任人 | 时限 |", "|---|---|---|"]
            for j in range(r.randint(3, 4)):
                b.append("| %s | %s | %d日内 |" % (pick(r, ZH_HEAD_A), pick(r, ["经办人", "主管", "管理员"]), r.randint(1, 4)))
        bl.append(b)
    return bl


# ---------------------------------------------------------------- meeting minutes (en)

MIN_TOP = ["queue migration", "capacity planning", "on-call rota", "vendor renewal", "storage costs", "dashboard cleanup",
           "access reviews", "build times", "incident follow-ups", "documentation debt", "hiring plan", "test flakiness"]
MIN_NOTE = ["Group agreed to revisit next month.", "No objections raised.", "Waiting on numbers from finance.", "Two people volunteered to draft a proposal.",
            "Concern raised about the reporting overhead.", "Short demo given; feedback was positive.", "Deferred until the next sync.",
            "Everyone to read the linked write-up first.", "Risk accepted for now; owner will monitor."]
MIN_NAMES = ["Anna Lindqvist", "Marcus Reyes", "Wei Zhang", "Olusegun Adeyemi", "Chloe Dubois", "Rahul Menon", "Sofia Marchetti", "Ben Hartley"]


def minutes_blocks(r, n_blocks=60, start_day=5):
    bl = []
    d = start_day
    mth = 1
    for i in range(n_blocks):
        d += r.randint(6, 9)
        while d > 28:
            d -= 28
            mth += 1
        b = ["", "## Sync of 2026-%02d-%02d" % (mth, d), "", "Attendees: " + ", ".join(r.sample(MIN_NAMES, 4)), ""]
        for t in r.sample(MIN_TOP, r.randint(2, 3)):
            b.append("- %s: %s" % (t, pick(r, MIN_NOTE)))
        b.append("- Action: %s to follow up on %s." % (pick(r, MIN_NAMES), pick(r, MIN_TOP)))
        bl.append(b)
    return bl


# ---------------------------------------------------------------- logs

COMP = ["sched", "cache", "http", "db", "queue", "auth", "gc", "net", "store", "sync"]
MSG_EN = {
    "sched": ["tick ok pending=%d", "lease renewed worker=w%d", "queue depth=%d"],
    "cache": ["evicted %d entries", "hit ratio %d%% (60s)", "warmup done keys=%d"],
    "http": ["GET /healthz 200 %dms", "POST /v1/sessions 201 %dms", "GET /v1/items 200 %dms"],
    "db": ["checkpoint wrote %d pages", "pool active=%d idle=6", "vacuum finished tables=%d"],
    "queue": ["consumer lag=%d", "acked batch size=%d", "rebalance took %dms"],
    "auth": ["token issued ttl=%ds", "login ok uid=u%d", "refresh ok uid=u%d"],
    "gc": ["pause %dms heap=212MB", "minor collection %dms", "heap resized to %dMB"],
    "net": ["peer p%d connected", "keepalive rtt=%dms", "resolved upstream in %dms"],
    "store": ["segment %d sealed", "compaction pass %d done", "snapshot %d uploaded"],
    "sync": ["delta applied n=%d", "cursor advanced to %d", "idle, next poll in %ds"],
}
MSG_ZH = {
    "sched": ["轮询完成 待处理=%d", "续租成功 w%d", "队列深度=%d"],
    "cache": ["淘汰 %d 条", "命中率 %d%%", "预热完成 %d"],
    "http": ["GET /healthz 200 %dms", "POST /v1/orders 201 %dms", "GET /v1/items 200 %dms"],
    "db": ["检查点写入 %d 页", "连接池 活跃=%d", "清理完成 %d"],
    "queue": ["消费积压=%d", "批量确认 %d", "重平衡 %dms"],
    "auth": ["签发令牌 %ds", "登录成功 u%d", "刷新成功 u%d"],
    "gc": ["停顿 %dms 堆=212MB", "回收 %dms", "堆扩容至 %dMB"],
    "net": ["节点 p%d 已连接", "心跳往返 %dms", "上游解析 %dms"],
    "store": ["分段 %d 已封存", "合并第 %d 轮完成", "快照 %d 已上传"],
    "sync": ["增量应用 %d", "游标推进至 %d", "空闲 %d 秒"],
}


def log_lines(r, n, lang="en", fmt="app", day=(2026, 9, 14), start_sec=0, avoid=()):
    """n single-line entries with monotone timestamps; fmt app | syslog."""
    msgs = MSG_ZH if lang == "zh" else MSG_EN
    t = start_sec
    out = []
    times = []
    for _ in range(n):
        t += r.randint(1, 9)
        times.append(t)
        h, m, s = t // 3600 % 24, t // 60 % 60, t % 60
        c = pick(r, COMP)
        msg = pick(r, msgs[c]) % r.randint(2, 480)
        lvl = "INFO" if r.random() < 0.95 else "DBG"
        if fmt == "syslog":
            out.append("Sep %2d %02d:%02d:%02d db01 %s %s" % (day[2], h, m, s, c, msg))
        else:
            out.append("%02d:%02d:%02d %s %s: %s" % (h, m, s, lvl, c, msg))
    return out, times


def stamp(fmt, day, t):
    h, m, s = t // 3600 % 24, t // 60 % 60, t % 60
    if fmt == "syslog":
        return "Sep %2d %02d:%02d:%02d" % (day[2], h, m, s)
    return "%02d:%02d:%02d" % (h, m, s)


def log_with_plants(r, n, plants, lang="en", fmt="app", day=(2026, 9, 14), start_sec=0):
    """plants: list of (index, fn(stamp_str) -> line or list of lines); indexes refer to the filler list."""
    base, times = log_lines(r, n, lang, fmt, day, start_sec)
    out = []
    pl = {i: f for i, f in plants}
    for i, l in enumerate(base):
        if i in pl:
            x = pl[i](stamp(fmt, day, times[i]))
            out.extend(x if isinstance(x, list) else [x])
        out.append(l)
    return out


# ---------------------------------------------------------------- configs

SVC = ["billing", "catalog", "search", "mailer", "notify", "inventory", "reports", "media", "geo", "profile", "tagging", "export", "audit", "scheduler"]
ENVS = ["dev", "qa", "canary", "demo"]
YKEY = [("replicas", lambda r: r.randint(1, 6)), ("cpu_limit", lambda r: "%dm" % (r.randint(2, 16) * 250)),
        ("memory_mb", lambda r: r.randint(2, 16) * 256), ("log_level", lambda r: pick(r, ["info", "warn", "debug"])),
        ("timeout_s", lambda r: r.randint(3, 40)), ("batch_size", lambda r: r.randint(2, 20) * 10),
        ("feature_x", lambda r: pick(r, ["true", "false"])), ("retries", lambda r: r.randint(0, 5))]


def yaml_blocks(r, n_blocks=70, avoid=()):
    bl = []
    for i in range(n_blocks):
        s = pick(r, [x for x in SVC if x not in avoid])
        e = pick(r, ENVS)
        b = ["", "%s-%s:" % (s, e)]
        for k, g in r.sample(YKEY, r.randint(5, 7)):
            b.append("  %s: %s" % (k, g(r)))
        bl.append(b)
    return bl


INI_SEC = ["logging", "metrics", "tracing", "mailer", "uploads", "sessions", "ratelimit", "cors", "static", "scheduler", "search", "imaging", "export", "locale"]
INI_KEY = [("enabled", lambda r: pick(r, ["true", "false"])), ("level", lambda r: pick(r, ["info", "warn", "error"])),
           ("max_items", lambda r: r.randint(2, 40) * 25), ("flush_every", lambda r: r.randint(2, 30)),
           ("path", lambda r: "/var/lib/app/%s" % pick(r, ["spool", "cache", "tmp", "out"])), ("workers", lambda r: r.randint(1, 8)),
           ("prefix", lambda r: pick(r, ["app_", "svc-", "x_"])), ("buffer_kb", lambda r: r.randint(1, 16) * 64)]


def ini_blocks(r, n_blocks=70, avoid=()):
    bl = []
    used = set()
    for i in range(n_blocks):
        s = pick(r, [x for x in INI_SEC if x not in avoid])
        name = "%s%s" % (s, "" if s not in used else "_%d" % (i,))
        used.add(s)
        b = ["", "[%s]" % name]
        for k, g in r.sample(INI_KEY, r.randint(4, 6)):
            b.append("%s = %s" % (k, g(r)))
        bl.append(b)
    return bl


def toml_blocks(r, n_blocks=70, avoid=()):
    bl = []
    for i in range(n_blocks):
        s = pick(r, [x for x in INI_SEC if x not in avoid])
        b = ["", "[modules.%s_%d]" % (s, i)]
        for k, g in r.sample(INI_KEY, r.randint(4, 6)):
            v = g(r)
            if isinstance(v, str) and v not in ("true", "false"):
                v = '"%s"' % v
            b.append("%s = %s" % (k, v))
        bl.append(b)
    return bl


PKEY = ["timeout.ms", "retries", "pool.size", "batch.size", "ttl.seconds", "buffer.kb", "endpoint.region", "tls.enabled"]
PSVC = ["inventory", "shipping", "tax", "ledger", "notify", "catalog", "loyalty", "fraud", "invoice", "address"]


def props_blocks(r, n_blocks=70, avoid=()):
    bl = []
    for i in range(n_blocks):
        s = pick(r, [x for x in PSVC if x not in avoid])
        b = ["", "# %s client" % s]
        for k in r.sample(PKEY, r.randint(3, 5)):
            if k.startswith("endpoint"):
                v = pick(r, ["eu-west", "us-east", "ap-south"])
            elif k.startswith("tls"):
                v = pick(r, ["true", "false"])
            else:
                v = r.randint(2, 60) * 50
            b.append("%s.client.%s=%s" % (s, k, v))
        bl.append(b)
    return bl


# ---------------------------------------------------------------- code

NOUN = ["record", "entry", "batch", "ticket", "invoice", "session", "profile", "manifest", "segment", "payload", "cursor", "digest"]
ACT = ["normalize", "collect", "prune", "merge", "annotate", "flatten", "index", "rewrite", "split", "tally"]


def py_blocks(r, n_blocks=60, avoid=()):
    bl = []
    seen = set()
    for i in range(n_blocks):
        a, nn = pick(r, ACT), pick(r, NOUN)
        name = "%s_%s" % (a, nn)
        if name in seen or any(w in name for w in avoid):
            name += "_%d" % i
        seen.add(name)
        k1, k2 = pick(r, NOUN), pick(r, NOUN)
        t = r.random()
        if t < 0.4:
            b = ["", "", "def %s(item, *, strict=False):" % name, '    """%s one %s before it is stored."""' % (a.capitalize(), nn),
                 "    out = dict(item)", "    for key in (%r, %r):" % (k1, k2), "        if key in out and isinstance(out[key], str):",
                 "            out[key] = out[key].strip()", "    if strict and not out:", "        raise ValueError(\"empty %s\")" % nn, "    return out"]
        elif t < 0.75:
            b = ["", "", "def %s(items, limit=%d):" % (name, r.randint(2, 20) * 10), '    """Return at most `limit` %ss, %s first."""' % (nn, k1),
                 "    kept = []", "    for it in items:", "        if len(kept) >= limit:", "            break", "        if it.get(%r):" % k2,
                 "            kept.append(it)", "    return kept"]
        else:
            b = ["", "", "class %s%s:" % (a.capitalize(), nn.capitalize()), '    """Small helper that %ss %ss."""' % (a, nn), "",
                 "    def __init__(self, source):", "        self.source = source", "        self.count = 0", "",
                 "    def run(self):", "        self.count += 1", "        return list(self.source)"]
        bl.append(b)
    return bl


def go_blocks(r, n_blocks=60, avoid=()):
    bl = []
    seen = set()
    for i in range(n_blocks):
        a, nn = pick(r, ACT), pick(r, NOUN)
        name = a + nn.capitalize()
        if name in seen or any(w in name for w in avoid):
            name += str(i)
        seen.add(name)
        t = r.random()
        if t < 0.5:
            b = ["", "func %s(in []string) []string {" % name, "\tout := make([]string, 0, len(in))", "\tfor _, s := range in {",
                 "\t\ts = strings.TrimSpace(s)", "\t\tif s == \"\" {", "\t\t\tcontinue", "\t\t}", "\t\tout = append(out, s)", "\t}", "\treturn out", "}"]
        else:
            b = ["", "func (w *worker) %s(n int) int {" % name, "\tw.mu.Lock()", "\tdefer w.mu.Unlock()", "\tif n > w.cap {", "\t\tn = w.cap", "\t}",
                 "\tw.seen += n", "\treturn w.seen", "}"]
        bl.append(b)
    return bl


def js_blocks(r, n_blocks=60, avoid=()):
    bl = []
    seen = set()
    for i in range(n_blocks):
        a, nn = pick(r, ACT), pick(r, NOUN)
        name = a + nn.capitalize()
        if name in seen or any(w in name for w in avoid):
            name += str(i)
        seen.add(name)
        t = r.random()
        if t < 0.5:
            b = ["", "function %s(list, opts = {}) {" % name, "  const max = opts.max || %d;" % (r.randint(2, 20) * 10), "  const out = [];",
                 "  for (const it of list) {", "    if (out.length >= max) break;", "    if (it && it.%s) out.push(it);" % pick(r, NOUN), "  }", "  return out;", "}"]
        else:
            b = ["", "const %s = (x) => {" % name, "  if (x == null) return null;", "  const y = { ...x };", "  y.%s = String(y.%s || \"\").trim();" % (nn, nn),
                 "  return y;", "};"]
        bl.append(b)
    return bl
