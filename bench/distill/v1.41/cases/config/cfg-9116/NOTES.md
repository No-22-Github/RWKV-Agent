## Traps
- TR-DECOY: dev and staging sections carry other values (50, 100) and the .example file says 10.

## Reference solution
1. read_file config/limits.yaml
Final answer: prod 环境的 upload_max_mb 是 200 MB（dev 是 50，示例文件里的 10 不生效）。

## Why the answer is unique
The user names the file and the prod section; only one line matches.
Why bash is not the tool here: one named file and one fact, so read_file is the direct read. The turn forbids bash so the rows teach that bash being offered does not make it the default.

## Alternative phrasings
1. prod 的上传上限是多少 MB？看 config/limits.yaml。
2. limits.yaml 里生产环境 upload_max_mb 的值是什么？
3. 生产环境允许上传多大的文件（MB），配置在 config/limits.yaml。
4. 帮我看下 config/limits.yaml，prod 段的 upload_max_mb 是几？
5. config/limits.yaml 中 prod.upload_max_mb 等于多少？
