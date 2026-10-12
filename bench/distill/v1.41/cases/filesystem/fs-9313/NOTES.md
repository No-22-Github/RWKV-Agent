## Traps
- TR-READONLY: 站点/legacy-admin.html depends on the old jQuery plugin (README).
- TR-DECOY: /js/jquery-ui-1.12.1.min.js has a similar name and a 1.12 version, but is not jQuery core.

## Reference solution
1. bash: `find 站点 -name '*.html' | grep -v legacy-admin | xargs sed -i 's#/js/jquery-1\.12\.4\.min\.js#/js/jquery-3.7.1.min.js#'`
2. bash: `grep -rn 'jquery' 站点` to confirm the target files changed and the protected ones did not.
Final answer: DONE (home, docs, blog and shop load jquery-3.7.1; legacy-admin.html and jquery-ui are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. Switch the jquery script tag in the 站点 pages from 1.12.4 to 3.7.1, except the page the README keeps.
2. Replace jquery-1.12.4.min.js with jquery-3.7.1.min.js in every 站点 HTML except legacy-admin. DONE when finished.
3. 站点下的页面把 jquery 的引用从 1.12.4 换成 3.7.1，legacy-admin 和 jquery-ui 不动，改完回复 DONE。
4. Update the jQuery include to 3.7.1 on the four public pages, leave the admin page and jquery-ui alone.
5. 把公开页面的 jQuery 引用升级到 3.7.1 版本的文件，README 里的例外照办，回复 DONE。
