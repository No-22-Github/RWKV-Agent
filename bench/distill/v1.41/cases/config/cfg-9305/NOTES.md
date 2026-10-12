## Traps
- TR-READONLY: php/cli.ini keeps 128M (README).
- TR-DECOY: ;memory_limit = 128M is a commented copy and opcache.memory_consumption = 128 is another setting.

## Reference solution
1. bash: `find php -name '*.ini' | grep -v cli.ini | xargs sed -i 's/^memory_limit = 128M$/memory_limit = 256M/'`
2. bash: `grep -rn 'memory' php` to confirm the target files changed and the protected ones did not.
Final answer: DONE (fpm, web, admin and cron have memory_limit = 256M; cli.ini, the commented line and opcache are unchanged).

## Why the answer is unique
Only the files and lines the README allows change, every other byte stays identical (4 files change).

## Five alternative phrasings of the task
1. php 里 fpm、web、admin、cron 的 ini，memory_limit 改成 256M，cli 不动。
2. 把 128M 的 memory_limit 全部提高到 256M（只改生效的那行），README 里说保留的保留。
3. php/*.ini 批量调整内存上限为 256M，注释行和 opcache 的值别碰，完成回复 DONE。
4. PHP 的 memory_limit 从 128M 升到 256M，cli.ini 例外，改完回复 DONE。
5. Raise the active memory_limit from 128M to 256M in the php ini files except the CLI one, reply DONE.
