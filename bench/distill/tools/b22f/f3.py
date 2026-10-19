"""F3 helper: several 400-1200 line registers in the workspace -> one summary file.

Each document is a register of 6-line entries (id, level, status, owner, due, note). The task asks for
the entries that are level=high AND status=open (optionally for one owner); every other combination is
generated as a decoy, so a grep on one field is not enough and the answer needs the whole entry."""
import random

from common import T, est, mk
from gen import Gen

ZH_OWN = ["张伟", "李娜", "王磊", "陈静", "刘洋", "赵敏", "周杰", "吴婷", "郑凯", "孙悦", "马超", "朱琳"]
EN_OWN = ["Priya Nair", "Tom Becker", "Lena Ortiz", "Mark Evans", "Aiko Tanaka", "Sam Okoye", "Julia Frank", "Omar Haddad"]
ZH_TIT = ["{t}延期交付", "{t}预算超支", "{t}接口不稳定", "{t}人手不足", "{t}合规检查未通过", "{t}供应商变更", "{t}验收标准不明确", "{t}环境不稳定",
          "{t}文档缺失", "{t}交接不完整"]
EN_TIT = ["{t} delivery slips", "{t} budget overrun", "{t} interface unstable", "{t} understaffed", "{t} compliance check failed",
          "{t} supplier change", "{t} acceptance criteria unclear", "{t} environment flaky", "{t} documentation missing", "{t} handover incomplete"]


def register(rng, g, lang, prefix, n_entries, targets, topics, owners, labels, owner_filter=None):
    """Returns (text, target_ids, line_count). labels: dict(level, status, owner, due, note, hi, mids, open, closed, head)."""
    zh = lang == "zh"
    used, rows, tids = set(), [], []
    num = rng.randint(100, 180)
    pos = set(rng.sample(range(40, n_entries), targets)) if targets else set()
    for i in range(n_entries):
        num += rng.randint(2, 9)
        while num in used:
            num += 1
        used.add(num)
        eid = "%s-%d" % (prefix, num)
        own = rng.choice(owners)
        if i in pos:
            level, status = labels["hi"], labels["open"]
            if owner_filter:
                own = owner_filter
            tids.append(eid)
        else:
            while True:
                level = rng.choices([labels["hi"]] + labels["mids"], [2, 3, 3, 4][:1 + len(labels["mids"])])[0]
                status = rng.choice([labels["open"], labels["closed"]])
                if not (level == labels["hi"] and status == labels["open"] and (not owner_filter or own == owner_filter)):
                    break
        title = rng.choice(ZH_TIT if zh else EN_TIT).format(t=rng.choice(topics))
        due = "2026-%02d-%02d" % (rng.randint(1, 12), rng.randint(1, 28))
        rows.append(["### %s %s" % (eid, title), "%s%s" % (labels["level"], level), "%s%s" % (labels["status"], status),
                     "%s%s" % (labels["owner"], own), "%s%s" % (labels["due"], due), "%s%s" % (labels["note"], g.sentence()), ""])
    head = [labels["head"], "", ("共 %d 条记录，按编号顺序排列。" % n_entries) if zh else "%d entries in order of id." % n_entries, ""]
    lines = head + [x for r in rows for x in r]
    return "\n".join(lines) + "\n", tids, len(lines)


def F3(cid, lang, docs, topics, labels, prompt, out, owner_filter=None, seed=None, tt="write_structured", reads_est=4):
    """docs: [(path, prefix, n_entries, n_targets, title)]."""
    rng = random.Random("b22f-f3-%s" % (seed or cid))
    g = Gen("f3-" + (seed or cid), lang, topics)
    owners = ZH_OWN if lang == "zh" else EN_OWN
    files, all_ids, per_doc = {}, [], []
    for path, prefix, n, nt, title in docs:
        lab = dict(labels, head="# " + title)
        text, tids, nl = register(rng, g, lang, prefix, n, nt, topics, owners, lab, owner_filter)
        files[path] = text
        all_ids += tids
        per_doc.append(nl)
    assert all(400 <= n <= 1200 for n in per_doc), (cid, per_doc)
    late = 0
    for path, text in files.items():
        for line_no, line in enumerate(text.split("\n"), 1):
            if any_id(line, all_ids) and line_no > 200:
                late += 1
    assert late >= 3, (cid, late)
    # calibrated on a replay of doc-34551: list_files +240, search_text (200 hits) +1750, a 90-line read +1900 (zh) / ~1450 (en)
    window = 1900 if lang == "zh" else 1450
    et = 1500 + 450 + 250 + 1750 + reads_est * window + 200 + len(all_ids) * 30 + 200 + (reads_est + 3) * 300
    mk(cid, sub="F3", tt=tt, desc="Several long registers, merge the open high-level entries into one file", turns=[T(prompt, maxc=2000)],
       steps=("list_files 看各文件行数（%s）\nsearch_text / bash grep 定位级别为高的条目，再读对应位置确认状态%s\n"
              "read_file 用 start_line/end_line 读相关片段，约 %d 次\nwrite_file 写入 %s，列出 %d 个编号\n作答。" % (
                  "、".join("%s %d 行" % (p, n) for (p, *_), n in zip(docs, per_doc)), "和负责人" if owner_filter else "", reads_est, out, len(all_ids))),
       why="Target entries are the only ones with level high, status open%s; decoys differ in exactly one field." % (" and the named owner" if owner_filter else ""),
       est_tokens=et, files=files, rules={out: all_ids}, must=["list_files", "read_file", "write_file"], never=["web_search", "web_fetch"],
       traps=("TR-TRUNC", "TR-DECOY"), ref_calls=reads_est + 4, max_calls={"read_file": 12}, notes_extra="lines per document: %s" % per_doc)


def any_id(line, ids):
    return any(i in line for i in ids)
