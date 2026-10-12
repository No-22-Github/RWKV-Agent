## Traps
- TR-READONLY: charts/billing-legacy stays pinned (charts/README.md).
- TR-DECOY: sidecar `tag: v1.4.20` and `tag_hint: v1.4.2` look like the image tag; only the two-space-indented top-level `  tag: v1.4.2` line changes.

## Reference solution
1. bash: `find charts -name values.yaml | grep -v billing-legacy | xargs sed -i 's/^  tag: v1.4.2$/  tag: v1.5.0/'`
2. bash: `grep -rn 'tag' charts` to confirm the target files changed and the protected ones did not.
Final answer: DONE (api, web, worker and cron now use tag v1.5.0; billing-legacy and the sidecar and hint lines are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical.

## Five alternative phrasings of the task
1. Bump the image tag v1.4.2 to v1.5.0 in the values.yaml of each chart, except the pinned one; sidecars are separate. Verify and reply DONE.
2. In charts, change `tag: v1.4.2` under image to v1.5.0 for every service chart the README allows, then confirm and say DONE.
3. charts 下各个 values.yaml 的镜像 tag 从 v1.4.2 升到 v1.5.0，README 里说保持不变的别动，改完检查并回复 DONE。
4. Update the app image tag to v1.5.0 across charts/*/values.yaml (v1.4.2 only), leaving billing-legacy and the sidecar tags alone. Reply DONE once checked.
5. Please roll every chart's image tag forward from v1.4.2 to v1.5.0 except where charts/README.md says otherwise, check, and reply DONE.
