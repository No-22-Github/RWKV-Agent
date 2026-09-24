"""Training-corpus toolchain: teacher runs -> replay script -> harness-rendered rows.

    python3 -m scripts.corpus paths    --run <teacher run> ... --out script.jsonl
    python3 -m scripts.corpus render   --cases <bank> --script script.jsonl --out <dir>
    python3 -m scripts.corpus render   --records <normalized.jsonl> --out <dir>
    python3 -m scripts.corpus decontam --test bench/workbank/cases --candidates <bank>

Modules, from the bottom up:

- wire:       the assistant action bytes a script carries (tool call syntax);
- bank:       case banks on disk and normalized records as cases;
- script:     the replay script format shared with `agent-eval --script`;
- runs:       reading agent-eval run directories;
- paths:      picking teacher paths out of runs (was scripts/trace2script.py);
- render:     replaying a script through the eval harness (was scripts/harness_corpus.py);
- similarity: text features and scores behind decontam;
- decontam:   the test/distill overlap gate (was scripts/decontam.py).

Run from the repository root. Workflow and rules: docs/harness-corpus-render.md.
"""
