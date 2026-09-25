## Traps
- None. No trap tag is set: the constant has one definition in the workspace, and the entry point's import names the module that holds it.

## Reference solution
1. Read nightly.py: its first import takes TIDE_MARGIN_MINUTES from survey.limits (call 1).
2. Read survey/limits.py: the module defines TIDE_MARGIN_MINUTES, while survey/windows.py only imports it (call 2). The file that holds the definition is survey/limits.py.

## Why the answer is unique
survey/windows.py carries the name too, but as an import of the constant rather than a definition, and its own assignments are function parameters, so a reader who stops at the first module that mentions the name has not found a definition. Exactly one file assigns TIDE_MARGIN_MINUTES, and it is the file nightly.py imports it from, so the answer is survey/limits.py.
