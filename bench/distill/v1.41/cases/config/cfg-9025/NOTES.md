## Traps
- TR-READONLY: 服务/_模板 has the same registry.host line and stays as it is (服务/README.md).
- A global `s/reg-old.corp/reg.corp/` would also rewrite mirror.registry.host, which the README says does not migrate.
- Turn 2 reverts one service after turn 1 already changed it, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `find 服务 -name app.properties | grep -v /_模板/ | xargs sed -i 's/^registry\.host=reg-old\.corp$/registry.host=reg.corp/'`
2. bash: `grep -rn registry 服务` to confirm five services changed and 服务/_模板 and every mirror line did not.
Turn 2:
1. bash: `sed -i 's/^registry\.host=reg\.corp$/registry.host=reg-old.corp/' 服务/支付/app.properties`
2. bash: `grep -rn registry 服务`.
Final answers: DONE (turn 1: 六个服务里除模板外都改成 reg.corp；turn 2: 支付 已改回 reg-old.corp，其余不动).

## Why the answer is unique
Only the registry.host line of the named services changes; everything else is byte-identical to the fixture.
