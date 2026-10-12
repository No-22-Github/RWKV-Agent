## Traps
- TR-READONLY: web/vendor/widget.html still needs btn-old (NOTES.txt).
- TR-DECOY: btn-older starts with btn-old; a plain `s/btn-old/btn-main/` would turn it into btn-mainer.

## Reference solution
1. bash: `find web -type f | grep -v /vendor/ | grep -v NOTES | xargs sed -i 's/\bbtn-old\b/btn-main/g'`
2. bash: `grep -rn 'btn-' web` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four pages and site.css use btn-main; vendor/widget.html and btn-older are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (5 files change).

## Five alternative phrasings of the task
1. In web, change class btn-old to btn-main in every page and in site.css; vendor stays, btn-older is another class.
2. Replace the btn-old class name with btn-main across the HTML and CSS of our site (not the vendor folder). Reply DONE.
3. web 下的 html 和 css 里，类名 btn-old 全部换成 btn-main，vendor 目录和 btn-older 别动，完成回复 DONE。
4. Rename .btn-old to .btn-main in markup and stylesheet, skipping third-party vendor files, then say DONE.
5. 把网站里按钮类 btn-old 改名为 btn-main（含样式表），NOTES.txt 里说不能动的保持原样。
