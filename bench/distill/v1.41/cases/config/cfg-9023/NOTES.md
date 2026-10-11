## Traps
- TR-DECOY: 环境 prod-canary contains prod; `grep prod` also picks up the canary services (the sum would be 247). 部署/README.md says canaries are accounted separately.
- TR-DEFN: 备用副本数 lines also contain 副本数; resident replicas only is the question (adding the spare ones gives 239).
- TR-MULTISRC: 40 service directories, one values.yaml each.

## Reference solution
1. bash: `grep -lx '环境: prod' 部署/*/values.yaml | xargs grep -h '^副本数: ' | awk '{s+=$2} END{print s}'`
Final answer: 线上正式环境（prod）的常驻副本一共 195 个，金丝雀和备用副本没有算在内。

## Why the answer is unique
`grep -lx` selects files whose 环境 line is exactly prod; the anchored `^副本数: ` pattern skips 备用副本数.
