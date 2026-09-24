"""Model-visible text features and overlap scores for the decontamination gate.

A case is reduced to three feature sets:

- prompt: word 5-gram shingles of the task prompt;
- files:  line 3-gram shingles of the fixture files;
- names:  distinctive identifiers (hyphenated or dotted names such as
          notify-hub, CHG-2193, ledger_sync.yaml) across prompt and files.

Prompts and names compare by Jaccard; files by containment of the candidate
in the test case, so a test fixture reused inside a larger candidate
workspace still counts.
"""

from __future__ import annotations

import collections
import re

KINDS = ("prompt", "files", "names")

WORD = re.compile(r"[a-z0-9]+")
NAME = re.compile(r"\b[A-Za-z][A-Za-z0-9]*(?:[-_.][A-Za-z0-9]+)+\b")
# Too common across any workspace task to count as a shared identity.
COMMON_NAMES = {"readme.md", "e.g", "i.e"}

Features = dict[str, set]


def prompt_of(case: dict) -> str:
    return "\n".join(turn.get("prompt", "") for turn in case.get("turns", []))


def word_shingles(text: str, size: int = 5) -> set:
    words = WORD.findall(text.lower())
    return {tuple(words[i:i + size]) for i in range(max(0, len(words) - size + 1))}


def line_shingles(files: dict, size: int = 3) -> set:
    shingles = set()
    for content in files.values():
        lines = [line.strip() for line in str(content).splitlines() if line.strip()]
        shingles.update(tuple(lines[i:i + size]) for i in range(max(0, len(lines) - size + 1)))
        if 0 < len(lines) < size:
            shingles.add(tuple(lines))
    return shingles


def names(case: dict) -> set:
    files = case.get("files") or {}
    text = prompt_of(case) + "\n" + "\n".join(str(v) for v in files.values()) + "\n" + "\n".join(files)
    return {name.lower() for name in NAME.findall(text)} - COMMON_NAMES


def features(case: dict) -> Features:
    return {"prompt": word_shingles(prompt_of(case)), "files": line_shingles(case.get("files") or {}),
            "names": names(case)}


def jaccard(left: set, right: set) -> float:
    return len(left & right) / len(left | right) if left and right else 0.0


def containment(part: set, whole: set) -> float:
    return len(part & whole) / len(part) if part else 0.0


SCORES = {"prompt": jaccard, "files": containment, "names": jaccard}


def scores(candidate: Features, test: Features) -> dict[str, float]:
    return {kind: SCORES[kind](candidate[kind], test[kind]) for kind in KINDS}


def boilerplate(population: list[Features], share: float) -> Features:
    """Features present in more than share of the population, per kind."""
    limit = share * len(population)
    common = {}
    for kind in KINDS:
        counts = collections.Counter(feature for item in population for feature in item[kind])
        common[kind] = {feature for feature, count in counts.items() if count > limit}
    return common


def strip(item: Features, common: Features) -> Features:
    return {kind: item[kind] - common[kind] for kind in KINDS}
