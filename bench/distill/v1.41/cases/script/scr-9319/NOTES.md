## Traps
- TR-READONLY: bin/vendor-install.sh is a third-party copy (README).
- TR-DECOY: The echoed sentence contains `which` and `whichever` as plain text; only lines that start with which change.

## Reference solution
1. bash: `find bin -name '*.sh' | grep -v vendor-install | xargs sed -i 's/^\( *\)which /\1command -v /'`
2. bash: `grep -rn 'which\|command -v' bin` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four scripts use command -v for docker and git; vendor-install.sh and the echoed texts are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. bin 里各脚本开头的 which docker / which git 改成 command -v，第三方拷贝不要动。
2. 把检查命令存在性的 which 全部替换成 command -v，提示文字里的词不改。
3. 批量把 bin/*.sh 行首的 which 换成 command -v，vendor-install.sh 除外，改完回复 DONE。
4. 脚本可移植性整改：which → command -v（只改命令位置），README 里说不动的保持原样。
5. Replace the line-leading which with command -v in the bin scripts except the vendored one, reply DONE.
