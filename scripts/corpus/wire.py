"""Assistant action bytes as a replay script carries them.

A script holds each generation's raw text; the student's wire (System block,
receipts, reminders) comes from the harness at render time. The only wire
knowledge the Python side needs is how an action is spelled. This matches
the work-v1 corpus renderer and the harness write-back: name first, compact
JSON, non-ASCII kept.
"""

from __future__ import annotations

import json

TOOL_CALL_OPEN = "<tool_call>"
TOOL_CALL_CLOSE = "</tool_call>"


def tool_call(name: str, arguments: dict) -> str:
    payload = json.dumps({"name": name, "arguments": arguments}, ensure_ascii=False, separators=(",", ":"))
    return f"{TOOL_CALL_OPEN}{payload}{TOOL_CALL_CLOSE}"
