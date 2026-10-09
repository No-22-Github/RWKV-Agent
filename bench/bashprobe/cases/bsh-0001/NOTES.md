11 Python files across 4 nested dirs; README.md under src/app is not .py. Answer 608.

Reference bash:

    find src -name '*.py' | xargs wc -l | tail -1

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
