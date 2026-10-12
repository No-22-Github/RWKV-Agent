## Traps
- TR-READONLY: i18n/_template.properties is not to be edited (NOTES.md).
- TR-DECOY: promo.banner.link starts with promo.banner but is a separate key that stays.

## Reference solution
1. bash: `find i18n -name '*.properties' | grep -v _template | xargs sed -i '/^promo\.banner=/d'`
2. bash: `grep -rn promo i18n` to confirm the target files changed and the protected ones did not.
Final answer: DONE (zh-CN, en-US, fr-FR and de-DE no longer have promo.banner; promo.banner.link and the template are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. Remove the promo.banner key from all locale files in i18n, but keep promo.banner.link and the template.
2. i18n/*.properties: drop the line starting with promo.banner= (the spring sale text), reply DONE.
3. 活动结束了，把 i18n 各语言文件里的 promo.banner 那一行删掉，其余的包括 link 和模板都不动。
4. Delete the spring banner entry from the four locale files; the template and the link key stay. Say DONE.
5. Clean up the ended promo: strip `promo.banner=` lines from the locales, per i18n/NOTES.md, then reply DONE.
