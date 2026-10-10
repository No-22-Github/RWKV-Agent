## Traps
- TR-DECOY: yarn.lock 里 preset-env 是 7.24.8，且 scripts 里两项现值都是 7.22.5，改错项的话文件会不一致。

## Reference solution
1. 读依据 yarn.lock，取出新值 7.25.2。
2. 读 scripts/versions.js：要改的是第 2 行「babelCore: '7.22.5'」。
3. replace_lines 第 2 行为「babelCore: '7.25.2'」（同行其余内容和格式不动）。
4. 回读 scripts/versions.js 确认。
终答示例：scripts/versions.js 的 babelCore 已从 7.22.5 改为 7.25.2，取自 yarn.lock；babelPresetEnv 没动。
判据：目标文件逐字节等于预期。

## Why the answer is unique
依据里符合条件的条目只有一条，目标行只有一行，替换后全文唯一。
