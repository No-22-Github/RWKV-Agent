## Traps
- TR-READONLY: 部署/归档/ also has 读超时秒: 30 and must stay.
- 写超时秒: 30 shares the text '超时秒: 30'; an unanchored sed changes it too. Services already at 45 stay at 45.
- 6 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 部署 -name 配置.yaml -not -path '*/归档/*' | xargs sed -i 's/^读超时秒: 30$/读超时秒: 60/'`
2. bash: `grep -rn 超时秒 部署`
Final answer: 已把在用服务里 读超时秒: 30 的改成 60，写超时和原本 45 的没动，归档目录未改。检查过了。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
