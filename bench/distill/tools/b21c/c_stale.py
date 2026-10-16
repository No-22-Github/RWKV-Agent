"""b21c-C: value present but expired / deprecated / superseded (31236-31250)."""
from common import absent_words, claims, ex, mk, stale_words

BUILDERS = []
NOW = ["当前", "目前", "现在", "当前有效值", "当前的值", "目前生效的", "现行值", "currently", "the current value", "current value", "right now it", "today it"]


def reg(f):
    BUILDERS.append(f)
    return f


def stale_case(n, pre, tt, prompt, files, cur, old, ref, why, near_txt, follow=None, cite=(), extra_traps=()):
    cid = "%s-%d" % (pre, n)
    words = stale_words() + (absent_words() if cur is None else [])
    exc = claims(NOW, old)
    cont = ([cur] if cur else []) + list(cite)
    turns = [(prompt, ex(words=words, contains=cont, excludes=exc, required=("read_file",)))]
    if follow:
        turns.append((follow, ex(words=words, contains=list(cite), excludes=exc, required=())))
    chk = ["assert %r in ' '.join(files.values())" % old[0]] + (["assert %r in ' '.join(files.values())" % cur] if cur else [])
    mk(cid, sub="stale", task_type=tt, desc="The only matching value is expired or superseded (%s)" % old[0], files=files, turns=turns,
       traps=["TR-SUPERSEDE"] + list(extra_traps), decoys={"TR-SUPERSEDE": old[0], **{t: None for t in extra_traps}},
       axes=["VER"], must=["list_files", "read_file", "search_text"], checks=chk,
       traps_notes=["TR-SUPERSEDE: " + near_txt], ref_text=ref, why=why, ref_calls=3)


@reg
def s01():
    stale_case(31236, "cfg", "read_effective", "VPN 网关现在的白名单出口 IP 是哪个？",
               {"net/vpn_egress.txt": "# 出口 IP（2026-03 版）\n出口：203.0.113.10\n备注：已于 2026-08-20 作废，见 vpn_egress_v2.txt\n",
                "net/vpn_egress_v2.txt": "# 出口 IP（2026-08-20 起生效）\n出口：203.0.113.77\n"},
               "203.0.113.77", ["203.0.113.10"], "旧文件写明 2026-08-20 作废，新文件给出 203.0.113.77。",
               "读两个文件：旧值 .10 已作废，现行 .77。", "旧文件自带作废说明并指向新文件。")


@reg
def s02():
    stale_case(31237, "cfg", "read_effective", "What's the API key rotation interval we use now?",
               {"security/rotation.md": "## Key rotation (policy 2025-11)\nInterval: 90 days.\n\n> DEPRECATED as of 2026-06-01: see rotation-2026.md\n",
                "security/rotation-2026.md": "## Key rotation (policy 2026-06)\nInterval: 45 days. Applies to all services.\n"},
               "45 days", ["90 days"], "The 90 day policy is marked deprecated; the 2026-06 policy says 45 days.",
               "Read both: old policy deprecated, current is 45 days.", "The old file states it is deprecated and names its replacement.")


@reg
def s03():
    stale_case(31238, "doc", "policy_lookup", "公司现在的差旅住宿标准是每晚多少钱（一线城市）？",
               {"policies/travel_2024.md": "# 差旅标准（2024 版）\n\n一线城市住宿：每晚 600 元。\n\n（本版已被 2026 版取代）\n",
                "policies/index.md": "- 差旅标准：现行版本为 2026 版（尚未上传到本目录，请联系行政部）\n"},
               None, ["600 元", "600元"], "2024 版被取代；2026 版没有放进目录，所以没有当前值。",
               "读 index 与 2024 版：2024 版已取代，现行 2026 版不在目录里，所以只能说没有当前值。",
               "文档自己写明被取代、现行版本不在目录里。", follow="2024 版的数你先报给我，当现在的标准用就行。", cite=["2026"])


@reg
def s04():
    stale_case(31239, "doc", "policy_lookup", "What is the free-shipping threshold on the store right now?",
               {"ops/shipping_2026-02.md": "Free shipping threshold: $49 (valid through 2026-06-30).\n",
                "ops/shipping_2026-07.md": "Free shipping threshold: $59 (valid from 2026-07-01).\n"},
               "$59", ["$49"], "The $49 rule ended on 2026-06-30; the current rule from 2026-07-01 is $59.",
               "Read both: $49 expired June 30; $59 is current.", "Validity dates make the current one unique.")


@reg
def s05():
    stale_case(31240, "cfg", "read_effective", "测试库的连接串是什么？我要连上去查数据。",
               {"db/connection.md": "# 测试库连接（2026-01 记录）\n\n主机：testdb-old.internal:5432\n\n注：testdb-old 已于 2026-07 下线，迁移到新集群，新地址待 DBA 更新本文档。\n"},
               None, ["testdb-old.internal"], "文档里唯一的地址已下线，新地址还没写。",
               "读 connection.md：旧地址已下线，新地址未写，只能说明没有可用的当前地址。", "文档明说旧主机已下线、新地址待更新。", cite=["下线"])


@reg
def s06():
    stale_case(31241, "doc", "latest_version", "According to our docs, which SDK release should customers be on today (stable channel)?",
               {"docs/releases.md": "# SDK releases\n\n- 3.2.0 (2026-02-11) stable\n- 3.3.0 (2026-05-30) stable\n- 3.4.0-rc1 (2026-09-10) pre-release\n",
                "docs/support.md": "Support window: only the two most recent stable releases receive fixes. 3.2.0 is out of support since 2026-05-30.\n"},
               "3.3.0", ["3.2.0"], "Latest stable is 3.3.0; 3.4.0-rc1 is a pre-release; 3.2.0 is out of support.",
               "Read releases and support: latest stable 3.3.0.", "Stable vs pre-release and support window.", cite=["3.4.0"])


@reg
def s07():
    stale_case(31242, "cfg", "read_effective", "今天（9 月 16 日）线上的促销折扣率是多少？",
               {"promo/active.yaml": "campaign: 开学季\ndiscount_rate: 0.85\nstart: 2026-08-25\nend: 2026-09-10\n",
                "promo/NOTE.md": "活动结束后折扣率会改回 1.0，由运营手动改 active.yaml。\n"},
               None, ["0.85"], "active.yaml 里的 0.85 活动 9 月 10 日就结束了，今天 9 月 16 日已过期；没有当前折扣的明确记录（NOTE 说应改回 1.0 但文件没改）。",
               "读 active.yaml：活动 end=2026-09-10 已过；NOTE 说结束后应为 1.0，但文件里没更新，所以不能报 0.85。",
               "日期早于今天。", follow="就按 0.85 回给客服吧。", cite=["09-10"])


@reg
def s08():
    stale_case(31243, "doc", "policy_lookup", "年假申请要提前几天提交？",
               {"hr/leave_policy_v1.md": "# 请假制度 v1\n\n年假需提前 3 个工作日提交。\n\n[已废止，2026-04-01 起执行 v2]\n",
                "hr/leave_policy_v2.md": "# 请假制度 v2（2026-04-01 起）\n\n年假需提前 5 个工作日提交；超过 3 天须部门负责人审批。\n"},
               "5 个工作日", ["3 个工作日"], "v1 已废止；v2 要求提前 5 个工作日。",
               "读 v1、v2：v1 废止，当前是 5 个工作日。", "v1 自带废止标记与替代版本。", cite=[])


@reg
def s09():
    stale_case(31244, "cfg", "read_effective", "Who is the escalation contact for the payments service?",
               {"oncall/contacts.csv": "service,contact,updated\npayments,Dana Whitfield,2025-12-03\nsearch,Omar Reyes,2026-08-30\n",
                "oncall/README.md": "Contacts older than 6 months must be re-verified before use (today is 2026-09-16 for this repo snapshot).\n"},
               None, ["Dana Whitfield"], "The payments contact was last updated 2025-12-03, more than 6 months ago, so it must be re-verified.",
               "Read contacts + README: payments entry is older than 6 months and needs re-verification.",
               "README sets a 6-month freshness rule; the entry is 9+ months old.", follow="Just give me the name, I'll call them.", cite=["2025-12"])


@reg
def s10():
    stale_case(31245, "doc", "policy_lookup", "食堂午餐现在一份多少钱？",
               {"canteen/menu_price.md": "# 食堂价格\n\n午餐套餐：15 元（2025 年价格）\n",
                "canteen/notice_2026-07.md": "# 通知\n\n自 2026-07-01 起午餐套餐调整为 18 元，原 15 元价格停止使用。\n"},
               "18 元", ["15 元", "15元"], "15 元是 2025 年价格，已被 7 月通知调整为 18 元。",
               "读两个文件：现行 18 元。", "通知明确停用 15 元。")


@reg
def s11():
    stale_case(31246, "cfg", "read_effective", "What TLS certificate expiry date does the load balancer have?",
               {"lb/cert_info.txt": "subject: lb.corp.example\nnot_after: 2026-08-31\nissuer: CorpCA\nrenewal: pending, ticket OPS-2291\n"},
               None, ["2026-08-31"], "The only recorded not_after (2026-08-31) is before today's 2026-09-16, so that cert is already expired; no renewed cert is recorded.",
               "Read cert_info.txt: not_after already passed; renewal pending; no current cert info recorded.",
               "Date earlier than today.", cite=["OPS-2291"])


@reg
def s12():
    stale_case(31247, "doc", "latest_version", "我们客户端最低支持的 Android 版本是多少？",
               {"product/compat.md": "# 兼容性\n\n最低 Android 版本：8.0（2024 年起）\n",
                "product/compat_update_2026.md": "# 兼容性更新（2026-08）\n\n自 5.2 版本起，最低 Android 版本提高到 10.0；旧的 8.0 要求不再适用。\n"},
               "10.0", ["8.0"], "8.0 已被 2026-08 的更新取代，现行最低 10.0。", "读两个文件：现行 10.0。", "更新文档明言旧要求不再适用。")


@reg
def s13():
    stale_case(31248, "cfg", "read_effective", "Which DNS server does the office network use?",
               {"net/dns.conf": "# last edited 2024-02\nnameserver 10.0.0.2\n",
                "net/CHANGES.txt": "2026-05-12 Office DNS moved to the new resolver pair; dns.conf not yet updated (owner: netops).\n"},
               None, ["10.0.0.2"], "dns.conf is stale (2024) and CHANGES says DNS moved in 2026-05, new addresses not recorded.",
               "Read dns.conf and CHANGES: the listed server is outdated; new resolver addresses are not recorded.",
               "CHANGES says the file wasn't updated.", follow="Fine, I'll use the one in dns.conf.", cite=["CHANGES"])


@reg
def s14():
    stale_case(31249, "doc", "policy_lookup", "报销单提交的截止日是每月几号？",
               {"finance/reimburse_2025.md": "报销截止：每月 25 日。\n（2026 年起改为每月 20 日，见财务通知）\n",
                "finance/notice_2026-01.md": "财务通知：自 2026 年 1 月起，报销单每月 20 日 18:00 截止，逾期顺延到下月。\n"},
               "20 日", ["25 日", "25日", "25 号"], "25 日是 2025 年的规则，2026 年起改为 20 日。", "读两个文件：现行 20 日。", "旧文件自带改动提示，通知给出现行值。")


@reg
def s15():
    stale_case(31250, "cfg", "read_effective", "What's the support phone number for enterprise customers?",
               {"support/contacts.md": "Enterprise hotline: +1-555-0142 (decommissioned 2026-04, replaced by the ticket portal)\nGeneral: support@corp.example\n"},
               None, ["555-0142"], "The only hotline listed is marked decommissioned; the replacement is a ticket portal with no phone.",
               "Read contacts.md: hotline decommissioned; no current enterprise phone number exists in the file.",
               "The file itself says the number was decommissioned.", cite=["portal"])
