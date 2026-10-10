"""b10a (v1.4 M3 first batch: M2 + M3) settings; the writer itself is ../casegen.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

_batch = Batch(salt="b10a", author="llm:glm-5.3-flash-b10a", version="v1.4")

# S5 triage: 0/3 cases where the teacher, not the criteria, was wrong in all
# three runs. They are written as usual and then moved to cases-shelved, so a
# rebuild reproduces the same live set. Reasons are in reports/b10a.md.
SHELVED = {
    "cfg-8014": "三遍都把 4号柴窑 的雾化压力 0.32 MPa 当替代值报出（简报：不复述诱饵数值）",
    "doc-8010": "三遍都把总服务台的 600 册当替代值报出",
    "tab-8023": "三遍都报出继任区 Alder Park 的营收作替代",
    "tab-8024": "三遍都报出 Kestrel Yard East 的维修额作替代",
    "tab-8027": "三遍都报出 Old Mill Crossing 的充电费作替代",
    "cfg-8019": "两遍超 600 字或复述诱饵 90，一遍工具参数非法 JSON",
    "cfg-8031": "三遍终答都超过 600 字",
    "web-8033": "两遍复述过时二手价 1,250，一遍超 600 字",
    "hyb-8018": "v2 补跑仍 0/3：用论坛旧价算出总额或不抓官方页，一遍工具参数非法 JSON",
    "log-8011": "v2 补跑仍 0/3：三遍都复述诱饵条数「7 条」（2 号影棚的失败数）",
    "log-8032": "v2 补跑仍 0/3：老师只数 approved 交易，题面「card payments processed」口径有歧义，待重写",
    "tab-8036": "v2 补跑仍 0/3：老师报含残缺门店的总额并说明不完整，但不单报两家完整门店之和；判据偏窄，待重写",
}


def write_case(cid, **kw):
    _batch.write_case(cid, **kw)
    if cid in SHELVED:
        import shutil
        live = os.path.join(_batch.cases, _scen(cid), cid)
        shelf = os.path.join(os.path.dirname(_batch.cases), "cases-shelved", _scen(cid), cid)
        if os.path.isdir(shelf):
            shutil.rmtree(shelf)
        os.makedirs(os.path.dirname(shelf), exist_ok=True)
        shutil.move(live, shelf)


def _scen(cid):
    from casegen import SCEN
    return SCEN[cid.split("-")[0]]


def revised(changes):
    """write_case that bumps the listed cases to version 2 and records why in a
    NOTES Changelog section (S5 triage of the teacher runs: criteria fixes and
    case bugs). changes maps case id -> one-line changelog entry."""
    def wrapped(cid, **kw):
        if cid in changes:
            kw["version"] = 2
            entry = "## Changelog\n- v2：%s\n\n" % changes[cid]
            notes = kw["notes"]
            mark = "## Why the answer is unique"
            kw["notes"] = notes.replace(mark, entry + mark, 1) if mark in notes else notes.rstrip("\n") + "\n\n" + entry
        return write_case(cid, **kw)
    return wrapped
