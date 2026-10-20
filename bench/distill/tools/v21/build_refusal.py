#!/usr/bin/env python3
"""v2.1 "answer after the tools are refused" paths, built from passing teacher paths.

    python3 bench/distill/tools/v21/build_refusal.py prepare --batch v20/qwen --rows R.jsonl --out DIR [--limit N]
    rwkv-lab corpus render --script DIR/probe.jsonl ...         # placeholder replay (see refusal.sh)
    python3 bench/distill/tools/v21/build_refusal.py teacher --out DIR [--parallel 16]
    rwkv-lab corpus render --script DIR/script.jsonl ...        # final replay

The exam failure this targets: the harness disables the tools (a repeated call
is rejected, the answer stage begins) and the student emits another tool call
instead of answering. A source path is a passing teacher path whose output
before the final answer is a read-only tool call. The constructed path replays
the source up to that call, then repeats it k times (k=1: rejected, answer
stage; k=2: the repeat lands in the answer stage and gets the strict re-ask),
then the teacher's new answer. Every scripted output except that answer is
unsupervised: the source path already trains those steps.

prepare: picks sources, writes probe.jsonl (answer = placeholder) and
sources.jsonl (the teacher's chat history for the final step, from its trace).
teacher: reads the placeholder replay's prompt, turns the harness text after the
repeated call into chat messages, asks the teacher (tools offered but
tool_choice none, thinking on) and writes script.jsonl with the new answer and
its reasoning. Mutating tools are never repeated (a repeated write_file or
replace_lines is executed again, not rejected).
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
READ_ONLY = {"read_file", "list_files", "search_text", "read_lines", "data_query", "calculator",
             "datetime", "web_search", "web_fetch", "get_weather", "bash"}
BASH_MUTATES = re.compile(r">|\btee\b|\brm\b|\bmv\b|\bcp\b|\btouch\b|\bmkdir\b|sed\s+-i|\bchmod\b|\bln\b|\btar\b|\bgzip\b")
PLACEHOLDER = "PLACEHOLDER-ANSWER"
CALL = re.compile(r'^\s*<tool_call>(\{.*\})</tool_call>\s*$', re.S)


def parse_call(text):
    m = CALL.match(text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def repeatable(text):
    call = parse_call(text)
    if not call or call.get("name") not in READ_ONLY:
        return False
    if call["name"] == "bash" and BASH_MUTATES.search(call.get("arguments", {}).get("command", "")):
        return False
    return True


def last_final_calls(trace_paths):
    """case id -> list of (final text, request messages, tools) for its final-answer model calls."""
    out = {}
    for path in trace_paths:
        for line in open(path, encoding="utf-8"):
            e = json.loads(line)
            if e.get("kind") != "model_call":
                continue
            mc = e["model_call"]
            resp = mc.get("response") or {}
            if resp.get("finish_reason") != "stop":
                continue
            req = json.loads(mc["request"]["prompt"])
            out.setdefault(e["case_id"], []).append((resp.get("text", "").strip(), req))
    return out


def prepare(args):
    batch_dir = REPO / "local/runs/distill" / args.batch
    script = {json.loads(l)["case_id"]: json.loads(l) for l in open(batch_dir / "script.jsonl", encoding="utf-8")}
    passed = {json.loads(l)["meta"]["case_id"] for l in open(args.rows, encoding="utf-8")}
    wanted = {l.strip() for l in open(args.ids_file) if l.strip()} if args.ids_file else None
    traces = sorted(str(p) for p in batch_dir.glob("teacher-k*/trace.jsonl"))
    finals = last_final_calls(traces)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    probes, sources = [], []
    for sid in sorted(script, key=lambda s: hashlib.sha256((args.batch + s).encode()).hexdigest()):
        if sid not in passed or (wanted is not None and sid.rsplit("--p", 1)[0] not in wanted):
            continue
        entry = script[sid]
        outs = entry["outputs"]
        if len(outs) < 2 or parse_call(outs[-1]["text"]) or not repeatable(outs[-2]["text"]):
            continue
        base = sid.rsplit("--p", 1)[0]
        final = outs[-1]["text"].strip()
        match = [req for text, req in finals.get(base, []) if text == final]
        if not match:
            continue
        k = 1 if int(hashlib.sha256(sid.encode()).hexdigest(), 16) % 5 < 3 else 2
        new_id = base + "--p%d" % (10 + k)  # --p11: k=1, --p12: k=2
        context = [{"text": o["text"], "supervised": False} for o in outs[:-1]]
        repeats = [{"text": outs[-2]["text"], "supervised": False} for _ in range(k)]
        probes.append({"case_id": new_id, "outputs": context + repeats + [{"text": PLACEHOLDER, "supervised": True}]})
        sources.append({"case_id": new_id, "source": sid, "k": k, "repeat": outs[-2]["text"],
                        "original_final": final, "request": match[-1]})
        if args.limit and len(probes) >= args.limit:
            break
    with open(out / "probe.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(p, ensure_ascii=False) + "\n" for p in probes)
    with open(out / "sources.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(s, ensure_ascii=False) + "\n" for s in sources)
    print("sources", len(sources), "k=1", sum(s["k"] == 1 for s in sources), "k=2", sum(s["k"] == 2 for s in sources))


def harness_tail(prompt, repeat_text):
    """The harness text after the first repeated call, as (tool_response, [user texts]).
    A repeat inside the answer stage is not written back (the harness only
    appends its re-ask), so the last occurrence of the source call is the first repeat."""
    marker = "\n\nAssistant: " + repeat_text.strip()
    positions = [m.start() for m in re.finditer(re.escape(marker), prompt)]
    if len(positions) < 2:
        return None
    tail = prompt[positions[-1] + len(marker):]
    tail = tail.rsplit("\n\nAssistant:", 1)[0]
    parts = [x.strip() for x in tail.split("\n\nUser: ")[1:] if x.strip()]
    if not parts or not parts[0].startswith("<tool_response>"):
        return None
    tool = parts[0].removeprefix("<tool_response>").removesuffix("</tool_response>")
    return tool, parts[1:]


def openai_messages(messages):
    """The trace keeps tool calls flattened ({id, name, arguments})."""
    out = []
    for m in messages:
        m = dict(m)
        if m.get("tool_calls"):
            m["tool_calls"] = [c if "function" in c else {"id": c["id"], "type": "function",
                               "function": {"name": c["name"], "arguments": c["arguments"]}} for c in m["tool_calls"]]
            m.setdefault("content", "")
        out.append(m)
    return out


def ask(api_base, api_key, model, body):
    req = urllib.request.Request(api_base.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json",
                                          "User-Agent": "rwkv-agent-distill/2.1"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def teacher(args):
    out = Path(args.out)
    sources = [json.loads(l) for l in open(out / "sources.jsonl", encoding="utf-8")]
    probes = {json.loads(l)["case_id"]: json.loads(l) for l in open(out / "probe.jsonl", encoding="utf-8")}
    prompts = {}
    for line in open(out / "probe-render/run/trace.jsonl", encoding="utf-8"):
        e = json.loads(line)
        if e.get("kind") == "model_call":
            prompts[e["case_id"]] = e["model_call"]["request"]["prompt"]  # last call = the placeholder step
    api_base, api_key, model = os.environ["API_BASE"], os.environ["API_KEY"], args.model

    def one(src):
        cid = src["case_id"]
        prompt = prompts.get(cid)
        if prompt is None:
            return cid, None, "no replay"
        tail = harness_tail(prompt, src["repeat"])
        if not tail:
            return cid, None, "tail shape"
        if "tools are now unavailable" not in prompt[-2500:] and "have been disabled" not in prompt[-2500:]:
            return cid, None, "no answer stage"
        req = src["request"]
        messages = openai_messages(req["messages"])
        call = parse_call(src["repeat"])
        tool, users = tail
        messages.append({"role": "assistant", "content": "", "tool_calls": [{
            "id": "call_refusal", "type": "function",
            "function": {"name": call["name"], "arguments": json.dumps(call.get("arguments", {}), ensure_ascii=False)}}]})
        messages.append({"role": "tool", "tool_call_id": "call_refusal", "content": tool})
        if users:
            messages.append({"role": "user", "content": "\n\n".join(users)})
        tools = [t if "function" in t else {"type": "function", "function": t} for t in req.get("tools") or []]
        body = {"model": model, "messages": messages, "tools": tools, "tool_choice": "none",
                "temperature": 0.3, "top_p": 1, "max_tokens": 4096, "thinking": {"type": "enabled"}}
        if not body["tools"]:
            body.pop("tools")
            body.pop("tool_choice")
        for attempt in range(3):
            try:
                resp = ask(api_base, api_key, model, body)
                msg = resp["choices"][0]["message"]
                text = (msg.get("content") or "").strip()
                if msg.get("tool_calls") or "<tool_call>" in text or not text:
                    continue
                return cid, {"text": text, "reasoning": (msg.get("reasoning_content") or msg.get("reasoning") or "").strip()}, None
            except urllib.error.HTTPError as exc:
                err = "%s %s" % (exc, exc.read()[:300])
            except Exception as exc:  # noqa: BLE001
                err = str(exc)
        return cid, None, "teacher: " + (locals().get("err") or "tool call or empty answer")

    results, errors = {}, {}
    with concurrent.futures.ThreadPoolExecutor(args.parallel) as pool:
        for cid, answer, err in pool.map(one, sources):
            if answer:
                results[cid] = answer
            else:
                errors[cid] = err
    with open(out / "script.jsonl", "w", encoding="utf-8") as f:
        for cid in sorted(results):
            entry = probes[cid]
            entry["outputs"][-1] = {"text": results[cid]["text"], "supervised": True, "reasoning": results[cid]["reasoning"]}
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    summary = {}
    for v in errors.values():
        summary[v] = summary.get(v, 0) + 1
    print("answered", len(results), "errors", summary)
    json.dump(errors, open(out / "teacher-errors.json", "w"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--batch", required=True, help="run dir under local/runs/distill, e.g. v20/qwen or v21/main")
    p.add_argument("--rows", required=True, help="rendered rows.jsonl of that batch (passing cases)")
    p.add_argument("--out", required=True)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--ids-file", help="only these base case ids (v2.2: rebuild the refusals the work-v3 replay dropped)")
    t = sub.add_parser("teacher")
    t.add_argument("--out", required=True)
    t.add_argument("--model", default="Qwen/Qwen3.7-Flash")
    t.add_argument("--parallel", type=int, default=16)
    args = ap.parse_args()
    {"prepare": prepare, "teacher": teacher}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
