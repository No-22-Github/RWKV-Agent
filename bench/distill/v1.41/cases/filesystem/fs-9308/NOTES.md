## Traps
- TR-READONLY: 语言包/旧客户端 is read by already shipped clients under the old key (README).
- TR-DECOY: msg.btn.cancle.tip contains btn.cancle but is a different key the README leaves alone.

## Reference solution
1. bash: `find 语言包 -name '*.properties' | grep -v /旧客户端/ | xargs sed -i 's/^btn\.cancle=/btn.cancel=/'`
2. bash: `grep -rn 'cancle\|cancel' 语言包` to confirm the target files changed and the protected ones did not.
Final answer: DONE (zh-CN, en-US, ja-JP and ko-KR use btn.cancel; 旧客户端 and msg.btn.cancle.tip are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 把各语言包里的 btn.cancle 键名订正为 btn.cancel，旧客户端目录不动。
2. 语言包的键 cancle 拼错了，改成 cancel；提示用的那个键先不管。
3. 批量修正 .properties 里的 btn.cancle → btn.cancel（只改键名），README 里点名的除外。
4. 四种语言的取消按钮键名改正拼写，旧版客户端的包保持原样，完成回复 DONE。
5. Rename the key btn.cancle to btn.cancel in the language packs, skipping the old-client pack, reply DONE.
