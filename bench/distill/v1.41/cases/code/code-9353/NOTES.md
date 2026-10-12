## Traps
- TR-DECOY: test_main.py files hold two TODOs each (not counted, never edited per src/README.md) and `# todo:` in lowercase is not a marker. Turn 3 touches only utils.py and io.py; main.py keeps the owner tag.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for p in $(ls src); do [ -d src/$p ] && echo "$(cat src/$p/main.py src/$p/utils.py src/$p/io.py | grep -c '# TODO:') $p"; done`
Turn 2 (edit, reply DONE):
1. bash: `sed -i 's/# TODO:/# TODO(maya):/' src/billing/main.py src/billing/utils.py src/billing/io.py`
2. bash: `grep -rn 'TODO' src/billing`
Turn 3 (edit, reply DONE):
1. bash: `sed -i 's/# TODO(maya):/# TODO:/' src/billing/utils.py src/billing/io.py`
2. bash: `grep -rn 'TODO' src/billing`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. Which package has the most TODO markers (tests excluded)? Tag them TODO(maya), then un-tag utils.py and io.py.
2. Find the package with the most '# TODO:' lines and assign them to maya, except in utils.py and io.py afterwards.
3. Count TODO comments per package without test files; add (maya) to the winner's TODOs and then restore utils.py and io.py.
4. Top TODO package? Mark its TODOs as maya's, then maya hands back utils.py and io.py.
5. src 里哪个包的 '# TODO:' 最多（测试文件不算）？给它的 TODO 标上 maya，之后把 utils.py 和 io.py 的标记去掉
