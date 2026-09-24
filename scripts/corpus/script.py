"""The replay script format (internal/agent/eval/script.go).

One JSON object per line: {"case_id": ..., "outputs": [{"text", "supervised"}]}.
A distilled path of case <id> is scripted as "<id>--p<n>"; render resolves
it back to the bank case.
"""

from __future__ import annotations

PATH_SEPARATOR = "--p"


def path_id(case_id: str, number: int) -> str:
    return f"{case_id}{PATH_SEPARATOR}{number}"


def base_case_id(script_case_id: str) -> str:
    """The bank case a script entry replays: "<id>--p<n>" -> "<id>"."""
    return script_case_id.rsplit(PATH_SEPARATOR, 1)[0] if PATH_SEPARATOR in script_case_id else script_case_id


def entry(case_id: str, texts: list[str], supervised: list[bool] | None = None) -> dict:
    flags = supervised if supervised is not None else [True] * len(texts)
    return {"case_id": case_id, "outputs": [{"text": text, "supervised": flag} for text, flag in zip(texts, flags)]}

