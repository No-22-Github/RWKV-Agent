"""Deterministic filler prose for the b22f long fixtures.

Filler sentences carry no digits, so every number in a page comes from a hand-written fact.
Facts are placed by the case modules; this module pads sections, adds the page furniture
(navigation, related reading, comments, footer) and keeps every sentence unique per page.
"""
import random

from common import est

ZH_ACT = ["运维同事", "产品团队", "一线用户", "新入职的同事", "值班人员", "项目负责人", "外部合作方", "社区志愿者", "技术支持", "财务同事",
          "数据分析师", "培训讲师", "审核人员", "门店店长", "实验室成员", "学生代表"]
ZH_Q = ["比较稳妥", "相对省事", "容易被忽略", "值得提前准备", "需要多花一点时间", "并不复杂", "在实践中很常见", "往往取决于具体场景", "不太容易一次说清",
        "更适合循序渐进", "需要留意细节", "各有取舍"]
ZH_V = ["做一次简单的自查", "把相关记录整理出来", "和相关同事沟通一下", "对照现有的说明逐项核对", "留出足够的缓冲时间", "按流程逐步推进",
        "提前通知可能受影响的人", "保留好操作过程的截图", "把结论写进共享文档", "安排一次小范围的试用"]
ZH_W = ["每个季度", "每次迭代结束后", "月底", "平时", "遇到变更时", "例会前", "评审之前", "上线之前", "项目收尾时"]
ZH_T = [
    "在{a}看来，{t}这件事{q}，通常要结合{t2}一起考虑。",
    "关于{t}，{a}{w}都会{v}，这样后续排查时心里更有底。",
    "很多{a}反馈，{t}和{t2}之间的关系并不总是直观，所以{v}这件事{q}。",
    "如果遇到{t}方面的疑问，建议先{v}，再决定下一步怎么处理。",
    "{t}的处理方式{q}，不同团队的习惯也不太一样，{a}可以参考自己的实际情况。",
    "围绕{t}的讨论在内部持续了一段时间，目前形成的共识是：{v}比事后补救更稳妥。",
    "{w}，{a}都会回头看看{t}的整体情况，并把发现的问题记录下来。",
    "需要说明的是，{t}并不是孤立存在的，它与{t2}、{t3}都有联系，改动时最好一并考虑。",
    "对于刚接触{t}的{a}来说，最实用的做法是{v}，然后再逐步熟悉细节。",
    "有人问到{t}能不能和{t2}合并处理，答案要看具体的使用方式。",
    "在实际协作中，{a}经常需要在{t}与{t2}之间做取舍，这件事{q}。",
    "我们整理了一些常见做法：{v}，或者{v2}，两种方式都可以接受。",
    "{t}相关的说明文档会不定期更新，建议{a}{w}回来看看是否有补充。",
    "从使用体验上讲，{t}整体上还算顺手，但个别场景下{a}仍需要{v}。",
    "对于{t3}，现阶段没有统一的要求，{a}可以根据需要自行安排，必要时{v}。",
    "补充一点背景：{t}最初是为了减少{t2}带来的沟通成本，后来逐渐成了日常流程的一部分。",
    "不少{a}{w}会检查一遍{t}，发现异常就及时反馈，这个习惯很有帮助。",
    "请注意，{t}的细节可能随版本调整而变化，{a}在操作前{v}会更稳妥。",
]
ZH_NAV = ["首页", "产品", "文档", "价格", "博客", "社区", "下载", "关于我们", "联系我们", "帮助中心", "登录", "注册", "English"]
ZH_REL = ["{t}使用心得：从入门到熟练", "关于{t}的十个常见疑问", "{a}眼中的{t}", "{t}与{t2}怎么搭配更顺手", "我们是如何改进{t}的",
          "新手必读：{t}的基础概念", "年度回顾：{t}这一年", "{t}踩坑记录"]
ZH_NICK = ["小满", "阿杰", "林间", "老周", "晴天", "木木", "远山", "Kevin", "七月", "不吃香菜", "墨客", "北辰"]
ZH_CMT = ["写得挺细的，收藏了。", "请问{t}这一块有没有更详细的说明？", "我们团队也遇到过类似的情况，{v}确实有帮助。", "感谢分享，期待后续更新。",
          "{t}部分讲得比较清楚，不过{t2}能不能再展开一点？", "路过，学习了。", "同意楼上的看法，{t}确实容易被忽略。", "有没有人试过{v}？效果如何？"]
ZH_FOOT = ["本站内容仅供参考，具体以实际情况为准。转载请注明出处。", "版权所有，保留一切权利。如有疑问，请通过页面底部的联系方式与我们联系。",
           "隐私政策 | 使用条款 | 站点地图 | 订阅更新 | 备案信息"]

EN_ACT = ["operators", "product teams", "everyday users", "new hires", "on-call engineers", "project leads", "outside partners",
          "community volunteers", "support staff", "finance staff", "analysts", "trainers", "reviewers", "store managers", "lab members",
          "student representatives"]
EN_Q = ["is usually the safer choice", "tends to be overlooked", "is worth preparing for in advance", "takes a little extra time",
        "is less complicated than it sounds", "is common in practice", "depends on the situation", "is hard to sum up in one sentence",
        "works best when done step by step", "rewards attention to detail", "involves some trade-offs"]
EN_V = ["run a quick self-check", "collect the relevant records", "talk it over with the people involved", "go through the existing notes item by item",
        "leave a comfortable buffer", "work through the steps in order", "warn anyone who might be affected", "keep screenshots of what was done",
        "write the conclusion into the shared document", "try it on a small group first"]
EN_W = ["every quarter", "at the end of each iteration", "at month end", "as a rule", "whenever something changes", "during the weekly meeting",
        "before a review", "before anything goes live", "when a project wraps up"]
EN_T = [
    "From the point of view of {a}, {t} {q}, and it is normally considered together with {t2}.",
    "On the subject of {t}, {a} usually {v} {w}, which makes later troubleshooting easier.",
    "Many {a} report that the link between {t} and {t2} is not always obvious, so it helps to {v}.",
    "If a question about {t} comes up, it is best to {v} first and decide on the next step afterwards.",
    "How {t} is handled differs from team to team, and {a} can follow whatever suits their own situation.",
    "The discussion around {t} has gone on for a while; the current consensus is that to {v} beats fixing things afterwards.",
    "{w}, {a} look back over {t} as a whole and write down any problems they notice.",
    "It should be said that {t} does not exist in isolation; it is tied to {t2} and {t3}, so changes are best made together.",
    "For {a} who are new to {t}, the most practical habit is to {v} and then pick up the details gradually.",
    "Someone asked whether {t} can be merged with {t2}. ",
    "In day-to-day work, {a} often have to trade {t} off against {t2}, and that choice {q}.",
    "Two common habits are noted here: you can {v}, or you can {v2}. Both are acceptable.",
    "Documentation about {t} is updated from time to time, so {a} may want to look again {w} for additions.",
    "In terms of experience, {t} works fine overall, although in a few situations {a} still need to {v}.",
    "For {t3} there is no single rule at the moment; {a} can arrange things as needed and, if necessary, {v}.",
    "Some background: {t} was introduced to cut down the communication cost of {t2}, and it gradually became part of the routine.",
    "Quite a few {a} check {t} {w}; when something looks off they report it quickly, and that habit {q}.",
    "Please note that details of {t} may change between versions, so it is safer to {v} before you act.",
]
EN_NAV = ["Home", "Products", "Docs", "Pricing", "Blog", "Community", "Downloads", "About", "Contact", "Help Center", "Sign in", "Sign up", "中文"]
EN_REL = ["Notes on {t}: from beginner to comfortable", "Ten common questions about {t}", "{t} as seen by {a}", "Pairing {t} with {t2}",
          "How we improved {t}", "Start here: the basics of {t}", "Year in review: {t}", "{t}: lessons from the field"]
EN_NICK = ["mara_k", "devon", "t.okafor", "linh", "sam_w", "rowan", "pbell", "yuki", "ines", "gareth", "noor", "casey"]
EN_CMT = ["Nicely detailed, bookmarked.", "Is there more detail on {t} somewhere?", "We ran into something similar; to {v} did help.",
          "Thanks for sharing, looking forward to the next update.", "The {t} part is clear, but could you expand on {t2}?",
          "Just passing through, learned something.", "Agree with the comment above, {t} is easy to miss.", "Has anyone tried to {v}? How did it go?"]
EN_FOOT = ["Content on this site is for reference only; actual conditions govern. Please credit the source when reposting.",
           "All rights reserved. If you have questions, use the contact details at the bottom of the page.",
           "Privacy | Terms | Sitemap | Subscribe | Accessibility"]


class Gen:
    def __init__(self, seed, lang, topics):
        self.r = random.Random("b22f-%s" % seed)
        self.zh = lang == "zh"
        self.topics = list(topics)
        self.seen = set()
        self.A, self.Q, self.V, self.W, self.T, self.REL, self.NICK, self.CMT = (
            (ZH_ACT, ZH_Q, ZH_V, ZH_W, ZH_T, ZH_REL, ZH_NICK, ZH_CMT) if self.zh else
            (EN_ACT, EN_Q, EN_V, EN_W, EN_T, EN_REL, EN_NICK, EN_CMT))

    def sentence(self):
        for _ in range(200):
            r = self.r
            t, t2, t3 = r.sample(self.topics, 3)
            s = r.choice(self.T).format(a=r.choice(self.A), q=r.choice(self.Q), v=r.choice(self.V), v2=r.choice(self.V),
                                        w=r.choice(self.W), t=t, t2=t2, t3=t3)
            if s not in self.seen:
                self.seen.add(s)
                return s
        raise RuntimeError("sentence pool exhausted")

    def para(self, n=None):
        n = n or self.r.randint(3, 5)
        return (("" if self.zh else " ")).join(self.sentence() for _ in range(n)) if not self.zh else "".join(self.sentence() for _ in range(n))

    def fill_to(self, paras, tokens):
        """Append filler paragraphs to a list until est() of the joined text reaches tokens."""
        out = list(paras)
        while est("\n\n".join(out)) < tokens:
            out.append(self.para())
        return out

    def nav(self):
        pool = list(ZH_NAV if self.zh else EN_NAV)
        self.r.shuffle(pool)
        return " | ".join(pool[:self.r.randint(7, 10)])

    def related(self, n=5):
        out = []
        for _ in range(n):
            t, t2 = self.r.sample(self.topics, 2)
            out.append("- " + self.r.choice(self.REL).format(t=t, t2=t2, a=self.r.choice(self.A)))
        return "\n".join(dict.fromkeys(out))

    def comments(self, n=4):
        out = []
        for _ in range(n):
            t, t2 = self.r.sample(self.topics, 2)
            out.append("- **%s**：%s" % (self.r.choice(self.NICK), self.r.choice(self.CMT).format(t=t, t2=t2, v=self.r.choice(self.V)))
                       if self.zh else
                       "- **%s**: %s" % (self.r.choice(self.NICK), self.r.choice(self.CMT).format(t=t, t2=t2, v=self.r.choice(self.V))))
        return "\n".join(dict.fromkeys(out))

    def foot(self):
        return self.r.choice(ZH_FOOT if self.zh else EN_FOOT)

    def page(self, title, intro, sections, tokens, noise=True):
        """sections: list of (heading, [fact paragraphs]); filler is spread so the page reaches ~tokens.
        Furniture (nav, related, comments, footer) is added around the sections."""
        parts = ["# " + title]
        if noise:
            parts.append(self.nav())
        parts.append(intro)
        furniture = ("\n\n".join([("## 相关阅读" if self.zh else "## Related reading"), self.related(),
                                  ("## 读者评论" if self.zh else "## Comments"), self.comments(), self.foot()]) if noise else "")
        budget = tokens - est("\n\n".join(parts)) - est(furniture)
        per = max(1, budget // len(sections))
        body = []
        for head, facts in sections:
            paras = self.fill_to([], 0)  # empty
            # facts are interleaved with filler so they do not sit at the section start
            first = [self.para(self.r.randint(2, 3))]
            tail = []
            for f in facts:
                tail.append(f)
                tail.append(self.para(self.r.randint(2, 3)))
            chunk = ["## " + head] + first + tail
            chunk = self.fill_to(chunk, per)
            body.append("\n\n".join(chunk))
        text = "\n\n".join(parts + body)
        if furniture:
            text += "\n\n" + furniture
        return text.rstrip("\n") + "\n"
