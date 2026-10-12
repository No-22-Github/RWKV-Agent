## Traps
- TR-READONLY: 栈/旧版 keeps its 8080 mapping (栈/说明.md).
- TR-DECOY: "18080:8080" is the monitoring mapping and contains 8080 twice; only the leading host port 8080 of the main mapping changes.

## Reference solution
1. bash: `find 栈 -name docker-compose.yml | grep -v /旧版/ | xargs sed -i 's/- "8080:/- "8090:/'`
2. bash: `grep -rn '8080\|8090' 栈` to confirm the target files changed and the protected ones did not.
Final answer: DONE (the four live stacks publish 8090; 旧版 and the 18080 mappings are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. 栈 里各服务 compose 文件的宿主机端口 8080 换成 8090，旧版目录和监控端口别动。
2. docker-compose.yml 里对外的 8080 全部改成 8090，说明.md 里点名的不要改，完成回复 DONE。
3. 把 栈 下四个服务的 ports 映射从 8080:xx 调整为 8090:xx，容器端口保持，监控的 18080 不变。
4. 栈目录里的端口 8080 要让出来，改为 8090（只改左边的宿主机端口），改完回复 DONE。
5. Change the published host port 8080 to 8090 in the compose files under 栈, leave what the README protects, reply DONE.
