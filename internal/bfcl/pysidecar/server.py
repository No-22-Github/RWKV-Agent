#!/usr/bin/env python3
"""Persistent BFCL multi-turn execution sidecar.

The protocol deliberately exposes only session lifecycle and execution of calls
provided by the caller. Evaluation answer files are outside this process.
"""

from __future__ import annotations

import contextlib
import json
import re
import sys
import traceback
from dataclasses import dataclass
from typing import Any

from bfcl_eval.eval_checker.multi_turn_eval import multi_turn_utils


@dataclass
class Session:
    initial_config: dict[str, Any]
    involved_classes: list[str]
    long_context: bool
    test_entry_id: str
    model_name: str


SESSIONS: dict[str, Session] = {}

# Lazily loaded RWKV tokenizer, shared with the E5 context census so the runtime
# guard and the feasibility numbers cannot disagree.
TOKENIZER: Any = None
TOKENIZER_VOCAB_SHA256: str | None = None


def _load_tokenizer(vocab_path: str) -> tuple[Any, str]:
    global TOKENIZER, TOKENIZER_VOCAB_SHA256
    if TOKENIZER is not None:
        return TOKENIZER, TOKENIZER_VOCAB_SHA256 or ""
    import hashlib
    import importlib.util

    module_path = "third_party/rwkv-mobile/converter/rwkv_src/rwkv_tokenizer.py"
    spec = importlib.util.spec_from_file_location("rwkv_mobile_tokenizer", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load RWKV tokenizer implementation: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    digest = hashlib.sha256(open(vocab_path, "rb").read()).hexdigest()
    tokenizer = module.RWKV_TOKENIZER(vocab_path)
    probe = 'System: tokenizer verification\nAssistant: {"name":"pwd","arguments":{}}'
    if tokenizer.decode(tokenizer.encode(probe)) != probe:
        raise RuntimeError("RWKV tokenizer round-trip verification failed")
    TOKENIZER, TOKENIZER_VOCAB_SHA256 = tokenizer, digest
    return tokenizer, digest


def _safe_component(value: str) -> str:
    return re.sub(r"[-./:]", "_", value)


def _execute(session: Session, calls: list[str]) -> list[str]:
    # Some BFCL backends print diagnostics. Keep stdout reserved for JSONL IPC.
    with contextlib.redirect_stdout(sys.stderr):
        results, _ = multi_turn_utils.execute_multi_turn_func_call(
            func_call_list=calls,
            initial_config=session.initial_config,
            involved_classes=session.involved_classes,
            model_name=session.model_name,
            test_entry_id=session.test_entry_id,
            long_context=session.long_context,
            is_evaL_run=False,
        )
    return results


def _close_session(sid: str) -> None:
    session = SESSIONS.pop(sid, None)
    if session is None:
        return
    prefix = _safe_component(f"{session.model_name}_{session.test_entry_id}_")
    suffix = "_instance"
    for name in list(vars(multi_turn_utils)):
        if name.startswith(prefix) and name.endswith(suffix):
            delattr(multi_turn_utils, name)


def _handle(request: dict[str, Any]) -> dict[str, Any]:
    request_id = request.get("request_id")
    operation = request.get("op")
    if operation == "new":
        sid = str(request["sid"])
        if sid in SESSIONS:
            raise ValueError(f"session already exists: {sid}")
        session = Session(
            initial_config=request.get("initial_config") or {},
            involved_classes=list(request["involved_classes"]),
            long_context=bool(request.get("long_context", False)),
            test_entry_id=str(request.get("test_entry_id") or sid),
            model_name=f"rwkv_agent_sidecar_{sid}",
        )
        SESSIONS[sid] = session
        _execute(session, [])
        return {"request_id": request_id, "ok": True, "sid": sid}
    if operation == "execute":
        sid = str(request["sid"])
        session = SESSIONS.get(sid)
        if session is None:
            raise ValueError(f"unknown session: {sid}")
        calls = request.get("calls")
        if not isinstance(calls, list) or not all(isinstance(call, str) for call in calls):
            raise ValueError("calls must be a list of strings")
        return {
            "request_id": request_id,
            "ok": True,
            "sid": sid,
            "results": _execute(session, calls),
        }
    if operation == "count_tokens":
        tokenizer, digest = _load_tokenizer(str(request["vocab"]))
        prompt = request.get("prompt")
        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string")
        return {
            "request_id": request_id,
            "ok": True,
            "tokens": len(tokenizer.encode(prompt)),
            "vocab_sha256": digest,
        }
    if operation == "close":
        sid = str(request["sid"])
        _close_session(sid)
        return {"request_id": request_id, "ok": True, "sid": sid}
    if operation == "shutdown":
        for sid in list(SESSIONS):
            _close_session(sid)
        return {"request_id": request_id, "ok": True, "shutdown": True}
    raise ValueError(f"unsupported operation: {operation!r}")


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        request_id = None
        try:
            request = json.loads(line)
            request_id = request.get("request_id")
            response = _handle(request)
        except Exception as error:  # The Go client needs a structured failure.
            traceback.print_exc(file=sys.stderr)
            response = {
                "request_id": request_id,
                "ok": False,
                "error": f"{type(error).__name__}: {error}",
            }
        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()
        if response.get("shutdown"):
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
