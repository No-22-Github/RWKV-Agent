## Traps
- TR-READONLY: 手册/_草稿 stays as it is (README).
- TR-DECOY: The sentence “图片都放在 images/ 目录里” mentions images/ in prose, not in a link; a bare `s/images\//assets\/img\//` rewrites it.

## Reference solution
1. bash: `find 手册 -name '*.md' | grep -v /_草稿/ | grep -v README | xargs sed -i 's#\](images/#](assets/img/#g'`
2. bash: `grep -rn 'images\|assets' 手册` to confirm the target files changed and the protected ones did not.
Final answer: DONE (入门, 进阶, 部署 and 运维 link to assets/img/; _草稿 and the prose sentences are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 手册里的图片引用 ](images/ 统一改成 ](assets/img/，草稿目录不改。
2. images 目录移到 assets/img 下了，请同步更新四个手册页面里的图片链接，文字说明不用改。
3. 批量替换 markdown 图片路径前缀为 assets/img/，_草稿 和 README 里说明的保持原样，完成回复 DONE。
4. 手册图片路径从 images/xxx 改到 assets/img/xxx（只改链接），改完回复 DONE。
5. The images moved to assets/img/; update the image links in the four manual pages but not in the drafts folder.
