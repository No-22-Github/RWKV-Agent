## Traps
- TR-READONLY: 脚本/生成/ is pipeline output and stays.
- The comment line also names cache-a (port 6380); turn 1 changes only the 缓存地址 line.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 脚本 -name '*.sh' -not -path '*/生成/*' | xargs sed -i 's#^缓存地址=redis://cache-a\.lan:6379$#缓存地址=redis://cache-b.lan:6379#'`
2. bash: `find 脚本 -name '*.sh' -not -path '*/生成/*' | xargs sed -i '/^# 备用：/d'`
3. bash: `grep -rn -e 缓存地址 -e 备用 脚本`
Final answer: 四个脚本的缓存地址已换成 cache-b，备用注释行已删除，生成目录未改。grep 核对过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
