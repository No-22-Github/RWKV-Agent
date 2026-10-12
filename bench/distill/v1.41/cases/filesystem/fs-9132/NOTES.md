## Traps
- TR-DECOY: docs/_build holds generated .md copies (docs/README.md); .md.bak, .mdx and .txt files are not Markdown sources.

## Reference solution
Turn 1: read_file release/VERSION -> 3.8.1.
Turn 2:
1. bash: `find docs -name '*.md' | grep -v /_build/ | wc -l`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, read_file is the direct read. Turn 2 spans many files, where one pipeline beats opening them one by one.

## Five alternative phrasings of the task
1. Count the .md files in docs recursively, leaving out the generated ones.
2. How many Markdown pages does docs hold, excluding build output?
3. Total number of source .md files under docs?
4. Number of Markdown sources in the docs tree (not the _build folder).
5. docs 目录下（含子目录）有多少个 .md 源文件？
