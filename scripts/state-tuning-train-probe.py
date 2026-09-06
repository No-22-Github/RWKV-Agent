#!/usr/bin/env python3
"""state-tuning 微调回测探针：把训练集 prompt 打给微调/基线两个端点，按 action 标注对照输出。

用途：判定 state-merged 微调是否真的学到了训练集行为（call / abstain），
还是合并时把更新洗掉了；以及学到后是否只是记忆。

用法：
    export CF_ACCESS_CLIENT_ID=<CF-Access-Client-Id>
    export CF_ACCESS_CLIENT_SECRET=<CF-Access-Client-Secret>
    python3 scripts/state-tuning-train-probe.py                     # 两个端点都跑
    python3 scripts/state-tuning-train-probe.py --endpoint ft       # 只跑微调端点
    python3 scripts/state-tuning-train-probe.py --concurrency 16    # 默认 8

注意：CF 边缘会拦 python-urllib 默认 UA，脚本已带 curl UA；端点在高并发
新建连接时有 TLS 瞬断（与 bfcl 全量同款），脚本内置 4 次退避重试 + 断点续跑。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TRAIN = REPO / "datasets/state-tuning/train/train.jsonl"

ENDPOINTS = {
    "ft": ("https://api-129-7b.rwkvos.com/v1/batch/completions",
           "rwkv7-g1j-7.2b-20260831-ctx16384-state-merged"),
    "base": ("https://api-7b.rwkvos.com/v1/batch/completions",
             "rwkv7-g1j-7.2b-20260831-ctx16384"),
}


def call_once(url: str, model: str, prompt: str, max_tokens: int, timeout: int) -> str:
    body = json.dumps({
        "model": model, "contents": [prompt], "max_tokens": max_tokens,
        "temperature": 0.001, "top_k": 1, "top_p": 1.0,
        "stream": False, "chunk_size": 1,
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "User-Agent": "curl/8.7.1",  # CF WAF 拦默认 python UA
        "CF-Access-Client-Id": CLIENT_ID,
        "CF-Access-Client-Secret": CLIENT_SECRET,
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    ch = d["choices"][0]
    # 不同 stream 模式下字段位置可能不同，逐个兜底
    for path in (("delta", "content"), ("message", "content"), ("text",)):
        cur = ch
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                cur = None
                break
        if isinstance(cur, str):
            return cur
    raise ValueError(f"unrecognized response shape: {str(d)[:200]}")


def call_with_retry(url, model, prompt, max_tokens, timeout, tries=4):
    last = None
    for a in range(tries):
        try:
            return call_once(url, model, prompt, max_tokens, timeout)
        except Exception as e:  # TLS 瞬断 / 5xx / 超时都重试
            last = e
            time.sleep(1.5 * (a + 1))
    return f"__ERR__{last}"


def load_done(out_path: Path) -> dict:
    done = {}
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                d = json.loads(line)
                done[d["id"]] = d
    return done


def run_endpoint(tag: str, rows: list[dict], out_dir: Path, conc: int, max_tokens: int, timeout: int) -> Path:
    url, model = ENDPOINTS[tag]
    out_path = out_dir / f"{tag}.jsonl"
    done = load_done(out_path)
    todo = [r for r in rows if r["id"] not in done]
    print(f"[{tag}] {model}\n  已完成 {len(done)}，待跑 {len(todo)}（并发 {conc}）", flush=True)
    with out_path.open("a", encoding="utf-8") as sink, ThreadPoolExecutor(max_workers=conc) as ex:
        futs = {ex.submit(call_with_retry, url, model, r["prompt"], max_tokens, timeout): r for r in todo}
        for n, f in enumerate(as_completed(futs), 1):
            row = futs[f]
            out = f.result()
            rec = {"id": row["id"], "action": row["action"], "subtype": row["subtype"],
                   "lang": row["lang"], "output": out}
            sink.write(json.dumps(rec, ensure_ascii=False) + "\n")
            sink.flush()
            if n % 50 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)}", flush=True)
    return out_path


def classify(output: str) -> str:
    if output.startswith("__ERR__"):
        return "error"
    return "call" if "<tool_call>" in output else "abstain"


def summarize(tag: str, recs: dict[str, dict], rows: dict[str, dict]):
    print(f"\n===== [{tag}] 训练集回测 =====")
    by_action: dict[tuple, list] = {}
    for i, rec in recs.items():
        by_action.setdefault((rows[i]["action"], rows[i]["subtype"]), []).append(rec)
    # 总体：action 判定一致率
    total = len(recs)
    correct = sum(1 for i, rec in recs.items() if classify(rec["output"]) == rows[i]["action"])
    print(f"action 判定一致: {correct}/{total} = {correct/total:.1%}")
    for action in ("call", "abstain"):
        sel = [recs[i] for i in recs if rows[i]["action"] == action]
        if not sel:
            continue
        pred_call = sum(1 for rec in sel if classify(rec["output"]) == "call")
        label = "产出信封率" if action == "call" else "误产出信封率"
        print(f"  {action:<7} n={len(sel):<4} {label}={pred_call/len(sel):6.1%}")
    # abstain 按 subtype 细分
    print("  abstain 细分（ subtype: n, 误产出信封率, 错误示例 id ）:")
    subs = sorted({rows[i]["subtype"] for i in recs if rows[i]["action"] == "abstain"})
    for sub in subs:
        sel = [recs[i] for i in recs if rows[i]["action"] == "abstain" and rows[i]["subtype"] == sub]
        bad = [rec["id"] for rec in sel if classify(rec["output"]) == "call"]
        errs = [rec["id"] for rec in sel if classify(rec["output"]) == "error"]
        print(f"    {sub:<18} n={len(sel):<4} 误信封={len(bad)/len(sel):6.1%}  err={len(errs)}"
              + (f"  例: {bad[:3]}" if bad else ""))
    errs = [i for i, rec in recs.items() if rec["output"].startswith("__ERR__")]
    if errs:
        print(f"  ⚠ {len(errs)} 例请求失败（重试后仍失败）: {errs[:5]} ...")


def compare(recs_ft: dict, recs_base: dict, rows: dict):
    common = sorted(set(recs_ft) & set(recs_base))
    flips = []
    for i in common:
        pf, pb = classify(recs_ft[i]["output"]), classify(recs_base[i]["output"])
        if pf != pb:
            flips.append((i, rows[i]["action"], pb, pf))
    print(f"\n===== base → ft 行为翻转（共同 {len(common)} 例）=====")
    if not flips:
        print("无任何判定翻转")
        return
    by = {}
    for i, action, pb, pf in flips:
        by.setdefault((action, pb, pf), []).append(i)
    for (action, pb, pf), ids in sorted(by.items()):
        print(f"  {action} 题: {pb} → {pf} : {len(ids)} 例  例: {ids[:5]}")
    same = sum(1 for i in common if recs_ft[i]["output"] == recs_base[i]["output"])
    print(f"输出逐字相同: {same}/{len(common)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", choices=["ft", "base", "both"], default="both")
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=160)
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()

    global CLIENT_ID, CLIENT_SECRET
    CLIENT_ID = os_env("CF_ACCESS_CLIENT_ID")
    CLIENT_SECRET = os_env("CF_ACCESS_CLIENT_SECRET")

    rows_list = [json.loads(l) for l in TRAIN.read_text().splitlines() if l.strip()]
    rows = {r["id"]: r for r in rows_list}
    print(f"训练集: {len(rows_list)} 条  action: "
          f"{ {a: sum(1 for r in rows_list if r['action']==a) for a in ('call','abstain')} }")

    out_dir = REPO / "runs" / f"state-tuning-probe-{datetime.now():%Y%m%d-%H%M%S}"
    out_dir.mkdir(parents=True, exist_ok=True)
    tags = ["ft", "base"] if args.endpoint == "both" else [args.endpoint]

    recs = {}
    for tag in tags:
        run_endpoint(tag, rows_list, out_dir, args.concurrency, args.max_tokens, args.timeout)
        recs[tag] = load_done(out_dir / f"{tag}.jsonl")
        summarize(tag, recs[tag], rows)

    if len(recs) == 2:
        compare(recs["ft"], recs["base"], rows)
        print(f"\n产物目录: {out_dir}（ft.jsonl / base.jsonl，含原始输出，可重跑续传）")


def os_env(key: str) -> str:
    import os
    v = os.environ.get(key, "").strip()
    if not v:
        sys.exit(f"缺少环境变量 {key}；先 export CF_ACCESS_CLIENT_ID / CF_ACCESS_CLIENT_SECRET")
    return v


if __name__ == "__main__":
    main()
