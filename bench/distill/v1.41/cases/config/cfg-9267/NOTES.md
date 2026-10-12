## Traps
- TR-READONLY: 项目/_vendored stays. TR-DECOY: `"axios-retry": "0.21.1"` shares the version string with axios (a global `s/0.21.1/1.6.2/` changes it).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find 项目 -name package.json | grep -v /_vendored/ | xargs sed -i 's/"axios": "0\.21\.1"/"axios": "1.6.2"/'`
2. bash: `grep -rn axios 项目`
Final answer: DONE (五个项目 axios 为 1.6.2).
Turn 2:
1. bash: `sed -i 's/"axios": "1\.6\.2"/"axios": "0.21.1"/' 项目/结算/package.json 项目/后台/package.json`
2. bash: `grep -rn axios 项目`
Final answer: DONE (结算、后台回到 0.21.1，商城、报表、小程序是 1.6.2).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. 把 axios 升到 1.6.2（第三方拷贝和 axios-retry 除外），然后结算和后台再钉回 0.21.1
2. 项目依赖里 axios 0.21.1 全部升级，结算与后台因为支付 SDK 回退
3. axios 批量升级，之后后台和结算固定回旧版本
4. 升 axios 到 1.6.2，其中结算、后台改回 0.21.1
5. Bump axios to 1.6.2 in all projects, then pin settlement and admin back to 0.21.1.
