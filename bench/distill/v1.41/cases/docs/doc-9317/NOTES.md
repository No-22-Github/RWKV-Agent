## Traps
- TR-READONLY: posts/roadmap.md is still under review (README).
- TR-DECOY: The indented `    draft: true` inside the code sample is documentation, not front matter.

## Reference solution
1. bash: `ls posts/*.md | grep -v roadmap | grep -v README | xargs sed -i 's/^draft: true$/draft: false/'`
2. bash: `grep -rn 'draft' posts` to confirm the target files changed and the protected ones did not.
Final answer: DONE (launch, pricing, hiring and recap have draft: false; roadmap.md and the code sample lines are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. Publish the finished posts: change `draft: true` to `draft: false` in each post's front matter, except the one still in review.
2. In posts/, flip the draft flag to false for launch, pricing, hiring and recap only. Reply DONE.
3. 把 posts 里已经写完的文章 front matter 中的 draft 改成 false，roadmap 还在评审，其他不动，完成回复 DONE。
4. Set draft: false on the four ready posts, leave roadmap.md and the code samples alone, say DONE.
5. Mark the ready posts as published (draft: false) per posts/README.md, then reply DONE.
