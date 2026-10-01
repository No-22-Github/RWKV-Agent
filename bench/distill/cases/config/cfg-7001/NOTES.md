## Traps
- TR-PRECEDENCE: batch_size 在三层配置里都出现（defaults 100、site-hangzhou 250、instance-push-07 200）。只读到站点层会报 250，只读平台默认会报 100；README 写明生效顺序是 平台默认 < 站点覆盖 < 实例覆盖，实际生效 200。

## Reference solution
1. 读 README.md：三层配置的存放位置与生效顺序。
2. 依次读 config/defaults.ini、config/site-hangzhou.ini、config/instance-push-07.ini，后一层覆盖前一层：batch_size 100 → 250 → 200。
3. 终答只报数字 200。

## Why the answer is unique
decoy 250 停在站点层，但 instance-push-07.ini 同样定义了 batch_size，而 README 把实例层放在覆盖链末端，两层同时定义同名键时实例层必胜，所以 250 不成立。只读 defaults 得 100 的读法忽略了两层覆盖，同样不成立。答案只有 200。
