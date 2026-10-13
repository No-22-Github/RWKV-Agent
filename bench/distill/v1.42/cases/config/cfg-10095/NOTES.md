## Traps
- TR-READONLY: 应用/示例/ is the tutorial template and stays dev.
- 4 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find 应用 -name application.properties -not -path '*/示例/*' | xargs sed -i 's/^spring.profiles.active=dev$/spring.profiles.active=prod/'`
2. bash: `grep -rn profiles.active 应用`
Final answer: 四个应用已切到 prod，示例模板仍是 dev，grep 确认过。DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
