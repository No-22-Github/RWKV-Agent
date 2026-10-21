"""b21c shared helpers: case writer, word lists, claim-form builders."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, lines  # noqa: E402,F401

BATCH = Batch(salt="b21c", author="llm:claude-sonnet-b21c", version="v2.1", tool_catalog="agent-tool-v2.0")
META = {}

_ABS_ZH = ["没有", "没找到", "未找到", "找不到", "不存在", "缺少", "缺失", "未定义", "没定义", "没有配置", "未设置", "没设置", "没设",
           "未配置", "没配置", "查不到", "没查到", "查无", "没有记录", "未见", "无此", "未提供", "没提供", "未包含", "不包含",
           "没有出现", "未出现", "没看到", "没有看到", "未发现", "没发现", "未写", "没写", "没有写", "没有提到", "未提及", "没提到",
           "并无", "查找不到", "找不着", "没有这个", "没有这一项", "没有该", "无法找到", "无法查到", "没有对应", "没有相应", "不见"]
_ABS_EN = ["not found", "missing", "does not exist", "doesn't exist", "no such", "not defined", "not set", "isn't set", "is not set",
           "absent", "couldn't find", "could not find", "can't find", "cannot find", "didn't find", "did not find", "no entry",
           "not present", "isn't present", "is not present", "isn't defined", "is not defined", "not specified", "isn't specified",
           "not listed", "isn't listed", "no record", "no value", "not configured", "isn't configured", "there is no", "there's no",
           "not included", "isn't included", "not provided", "isn't provided", "no mention", "not mentioned", "don't have", "do not have",
           "doesn't contain", "does not contain", "doesn't have", "does not have", "doesn't define", "does not define", "doesn't set",
           "does not set", "nothing", "no file", "not there", "couldn’t find", "doesn’t exist", "isn’t set", "don’t have", "doesn’t have"]
_STALE_ZH = ["过期", "失效", "废弃", "弃用", "作废", "已被替代", "被替代", "被取代", "取代了", "被覆盖", "已覆盖", "覆盖了", "不再",
             "旧值", "旧版", "过时", "已更新", "已不适用", "不适用", "已停用", "已下线", "已废止", "淘汰", "不是最新", "不是当前",
             "不是现行", "早于", "已于", "旧的", "老的", "历史", "不是现在", "不是目前", "已经换", "已换", "替换", "停用", "到期", "已结束", "截止"]
_STALE_EN = ["expired", "deprecated", "outdated", "out of date", "out-of-date", "obsolete", "superseded", "replaced", "no longer",
             "stale", "overridden", "overrides", "retired", "old value", "not current", "not valid", "invalid", "legacy", "older",
             "earlier", "was valid", "ended", "lapsed", "decommissioned", "not the current", "isn't current", "is not current",
             "no longer valid", "previous", "prior", "outdated"]
_CONF_ZH = ["冲突", "不一致", "矛盾", "不同", "出入", "不符", "分歧", "不一样", "对不上", "各写", "各自", "两个值", "两处", "两份",
            "不统一", "有差异", "存在差异", "差异", "说法不一", "两种说法", "互相"]
_CONF_EN = ["conflict", "inconsistent", "disagree", "differ", "mismatch", "discrepan", "contradict", "doesn't match", "don't match",
            "does not match", "do not match", "not consistent", "two different", "different values", "differently", "doesn’t match",
            "don’t match", "conflicting", "inconsistency"]
_PRIO_ZH = ["优先", "为准", "以", "覆盖", "生效", "采用", "胜出"]
_PRIO_EN = ["precedence", "priority", "takes priority", "overrid", "wins", "takes effect", "effective", "authoritative", "prevails"]
_UNDEC_ZH = ["无法判定", "无法确定", "不能确定", "没法判断", "无法判断", "不确定", "需要确认", "需确认", "请确认", "无法断定", "说不准", "无法确认", "不清楚", "没有说明", "未说明", "没说"]
_UNDEC_EN = ["cannot determine", "can't determine", "cannot tell", "can't tell", "unclear", "not clear", "unable to determine",
             "need to confirm", "needs confirmation", "should confirm", "not sure", "no way to tell", "don't know which", "ambiguous",
             "isn't clear", "is not clear", "can’t tell", "can’t determine", "which one", "which is"]


def _caps(ws):
    out = []
    for w in ws:
        out += [w, w.capitalize()]
        if "'" in w:
            out += [w.replace("'", "’"), w.capitalize().replace("'", "’")]
    return list(dict.fromkeys(out))


def absent_words():
    return _caps(_ABS_ZH + _ABS_EN)


def stale_words():
    return _caps(_STALE_ZH + _STALE_EN)


def conflict_words(prio=False, undecided=False):
    ws = _CONF_ZH + _CONF_EN
    if prio:
        ws += _PRIO_ZH + _PRIO_EN
    if undecided:
        ws += _UNDEC_ZH + _UNDEC_EN
    return _caps(ws)


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def level_for(traps, ref_calls, n_files, multi):
    n = len(traps)
    if n == 0 and ref_calls <= 3:
        return "L0"
    if n == 1 and ref_calls <= 4:
        return "L1"
    if n == 2 and not multi and ref_calls <= 4 and n_files < 3:
        return "L2"
    if n >= 3 or (multi and n >= 1) or ref_calls >= 8:
        return "L3"
    if n == 2 or (n == 1 and (n_files >= 3 or ref_calls >= 5)):
        return "L2"
    raise ValueError("no level")


_FORMS = ["{s}是{v}", "{s}为{v}", "{s} 是 {v}", "{s} 为 {v}", "{s}：{v}", "{s}: {v}", "{s}={v}", "{s} = {v}", "{s}设为{v}",
          "{s}设置为{v}", "{s}的值是{v}", "{s}的值为{v}", "{s} is {v}", "{s} = {v}", "{s} was {v}", "{s} of {v}", "{s} equals {v}",
          "{s} set to {v}", "{s} is set to {v}", "{s}共{v}", "{s}合计{v}", "{s}是 {v}", "{s} 是{v}"]


def claims(subjects, vals):
    """Affirmative claim substrings: subject + verb + value (never a bare value)."""
    out = []
    for s in subjects:
        for v in vals:
            out += [f.format(s=s, v=v) for f in _FORMS]
    return list(dict.fromkeys(out))


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n"
            "files = case[\"files\"]\n" % d)


def mk(cid, *, sub, task_type, desc, files, turns, traps, decoys, axes, must, never=(), checks=(), traps_notes, ref_text, why,
       ref_calls=2, forbid=()):
    """turns: [(prompt, expect)]; checks: python assert lines run on `files` in verify."""
    multi = len(turns) > 1
    # about half of the cases carry no catalog constraint (odd ids): then no tool can be required
    if int(cid.split("-")[1]) % 2 == 1:
        k = (int(cid.split("-")[1]) // 2) % 3
        must = [["read_file"], ["read_lines"], ["search_text"]][k]
        if sub == "file":
            must = ["list_files"] + must
        if k != 0:
            turns = [(p, {a: b for a, b in e.items() if a != "required_tools"}) for p, e in turns]
    else:
        must = ["list_files", "read_file"] if sub == "file" else ["read_file"]
    level = level_for(traps, ref_calls, len(files), multi)
    union = []
    for _, e in turns:
        for w in e.get("output_contains_any", []):
            if w not in union:
                union.append(w)
    body = "\n".join(checks) + "\n" if checks else ""
    body += "print(json.dumps({\"expected_contains_any\": %s}, ensure_ascii=False))\n" % json.dumps(union, ensure_ascii=False)
    tl = [{"prompt": p, "expect": e} for p, e in turns]
    notes = "## Traps\n" + "".join("- %s\n" % t for t in traps_notes)
    notes += "\n## Reference solution\n" + ref_text.strip("\n") + "\n"
    notes += "\n## Why the answer is unique\n" + why.strip("\n") + "\n"
    if cid.split("-")[0] in ("web", "hyb"):
        p0 = turns[0][0]
        alts = [p0, "想确认一下：" + p0, p0 + "（简单说就行）", "麻烦帮我看看：" + p0, "再问一件事：" + p0]
        notes += "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, a) for i, a in enumerate(alts))
    BATCH.write_case(cid, desc=desc, task_type=task_type, family="b21c-%s-%s" % (sub, cid.split("-")[1]), level=level,
                     ref_calls=ref_calls, files=files, turns=tl, verify=guard(files) + body, notes=notes, traps=traps,
                     decoys=decoys, axes=list(axes), answer_style="natural",
                     tool_policy={"must_offer": list(must), "never_offer": list(never)} if (must or never) else None,
                     extra_tags={"batch": "b21c", "sub": sub})
    META[cid] = {"sub": sub, "zh": is_zh(" ".join(p for p, _ in turns)), "turns": len(turns), "level": level,
                 "pol": bool(must or never)}


def ex(*, words, contains=(), excludes=(), required=("read_file",), any_token=False):
    e = {"output_contains_any": list(words)}
    contains = [c for c in contains if len(c) > 1]  # single characters match anything
    bare = [c for c in contains if re.fullmatch(r"\d{1,4}(\.\d+)*", c)]
    token = False
    if bare:
        if all(c.isascii() for c in contains):
            token = True  # only numbers / ASCII identifiers: whole-token match
        else:
            contains = [c for c in contains if c not in bare]  # mixed with Chinese: drop bare numbers
    if contains:
        e["output_contains"] = list(contains)
        if token:
            e["output_contains_token"] = True
    if excludes:
        e["output_excludes"] = list(excludes)
    if required:
        e["required_tools"] = list(required)
    return e
