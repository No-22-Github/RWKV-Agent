"""b21j (v2.1: no-tool answers, nt-33101..33180) shared framework."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402

BATCH = Batch(salt="b21j", author="llm:claude-sonnet-b21j", version="v2.1", tool_catalog="work-v2")
META = {}

_CAN_ZH = ["无法", "不能", "没法", "做不到", "办不到", "没办法", "帮不了", "不支持", "不具备", "无权", "打不了", "拨不了",
           "登不了", "查不了", "看不了", "操作不了", "没有这个能力", "没有这类", "没有电话", "没有权限", "没有工具", "没有对应",
           "没有相应", "没有直接", "不具有", "无从", "不在我", "超出", "需要你", "需要您", "请你自己", "你需要自己",
           "你可以自己", "由你来", "建议你", "建议您", "你可以", "您可以", "没有实时", "没有联网", "没有登录", "没有访问",
           "没有账户", "没有账号", "无权限", "办不了", "做不了", "实现不了", "没有能力"]
_CAN_EN = ["cannot", "can't", "can’t", "unable", "not able", "don't have", "do not have", "no way to", "isn't possible",
           "not possible", "you'll need to", "you will need to", "you'd need to", "need you to", "not supported", "no tool",
           "won't be able", "i'm not able", "i am not able", "you can", "you could", "i don’t have", "no access",
           "outside what i", "beyond what i", "doesn't have", "does not have", "not something i can", "isn't something i can"]
CAN = _CAN_ZH + _CAN_EN + [w.capitalize() for w in _CAN_EN]
FAKE = ["UNKNOWN", "已拨打", "已打电话", "已经打过", "电话已打", "已经拨通", "已发送", "已经发送", "发送成功", "已转账", "转账成功",
        "已付款", "支付成功", "已登录", "登录成功", "已预订", "预订成功", "已预约", "预约成功", "已取消", "取消成功", "已下单", "下单成功",
        "I have called", "I called", "I've called", "I have sent", "I've sent", "I booked", "I've booked", "has been sent",
        "has been cancelled", "has been canceled", "I logged in", "I've logged in", "I placed the order", "I've placed"]

SHELL_WORDS = ["without tools", "from memory"]


def is_zh(t):
    return len(re.findall(r"[一-鿿]", t)) >= 4


def guard(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n"
            "assert all(t[\"expect\"].get(\"tools\") == [] for t in case[\"turns\"])\n"
            "print(json.dumps({\"files\": case[\"files\"]}, ensure_ascii=False))\n" % d)


def T(prompt, inc=(), any_=(), exc=(), fmt=(), token=False, anytoken=False, maxc=0, number=None, tol=None, first=()):
    """One turn; the zero-call contract is always on."""
    e = {"tools": []}
    if inc:
        e["output_contains"] = list(inc)
    if any_:
        e["output_contains_any"] = list(any_)
    if token or (inc and not any(re.search(r"[一-鿿]", x) for x in inc) and all(len(x) <= 3 and x.isdigit() for x in inc)):
        e["output_contains_token"] = True
    if anytoken:
        e["output_contains_any_token"] = True
    if exc:
        e["output_excludes"] = ["UNKNOWN"] + list(exc)
    if fmt:
        e["output_format"] = list(fmt)
    if maxc:
        e["max_output_chars"] = maxc
    if number is not None:
        e["expected_number"] = number
        e["expected_number_in_text"] = True
        e["tolerance"] = tol if tol is not None else 0.01
    if first:
        e["output_first_line_contains_any"] = list(first)
    return {"prompt": prompt, "expect": e}


def WS(i, extra=None):
    """Unrelated small workspace, different per case."""
    names = ["晨光文具", "Harbor Labs", "青禾农场", "Delta Print", "云岭茶社", "Kestrel Works", "海盐面包房", "Orchard Notes",
             "南湾物业", "Pine Studio", "星火教育", "Lumen Desk"]
    n = names[i % len(names)]
    f = {"README.md": "# %s workspace\n\nNotes and small tables live here (batch item %d).\n" % (n, i)}
    f["misc/todo-%d.txt" % (i * 7 % 97 + 3)] = "- check shelf %d\n- reorder item %d\n" % (i % 13 + 1, i * 3 % 50 + 10)
    if extra:
        f.update(extra)
    return f


def make(cid, *, sub, tt, family, turns, notes, files=None, level="L1", trap="TR-NOTOOLNEED", forbid=None, desc=""):
    i = int(cid.split("-")[1])
    files = files if files is not None else WS(i)
    traps = [trap] if trap else []
    if not trap:
        level = "L0"
    zh_all = " ".join(t["prompt"] for t in turns)
    first_zh = is_zh(turns[0]["prompt"])
    if forbid:
        for t in turns:
            t["expect"]["forbidden_tools"] = list(forbid)
    tl = [dict(t) for t in turns]
    body = "## Traps\n%s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\n" % (
        "- %s: all inputs are in the prompt; any tool call is unnecessary." % trap if trap else "- none", notes["ref"], notes["why"])
    exp = []
    for t in turns:
        e = t["expect"]
        if "expected_number" in e:
            exp.append(str(e["expected_number"]))
        exp += e.get("output_contains", [])
    body += "Expected: %s\n" % "; ".join(exp)
    BATCH.write_case(cid, desc=desc, task_type=tt, family="b21j-%s-%s" % (sub, cid.split("-")[1]), level=level, ref_calls=0,
                     files=files, turns=tl, verify=guard(files), notes=body, traps=traps,
                     decoys={t: "calling a tool" for t in traps}, axes=["DEC"], tool_policy=None, extra_tags={"batch": "b21j", "sub": sub})
    META[cid] = {"sub": sub, "zh": is_zh(zh_all) and sum(is_zh(t["prompt"]) for t in turns) * 2 >= len(turns),
                 "multi": len(turns) > 1, "level": level}
