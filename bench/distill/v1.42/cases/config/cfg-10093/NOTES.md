## Traps
- TR-READONLY: 服务/本地调试/.env stays debug.
- SQL_LOG_LEVEL=debug contains LOG_LEVEL=debug; an unanchored s/LOG_LEVEL=debug/ flips it.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 服务 -name .env -not -path '*/本地调试/*' | xargs sed -i 's/^LOG_LEVEL=debug$/LOG_LEVEL=info/'`
2. bash: `grep -rn LOG_LEVEL 服务`
Final answer: 四个服务的 LOG_LEVEL 已改为 info，SQL_LOG_LEVEL 和本地调试目录没动，grep 核对过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
