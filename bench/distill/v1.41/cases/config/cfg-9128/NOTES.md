## Traps
- TR-READONLY: features/frozen is never edited and new_ui_v2 must not flip (a `s/= false/= true/` would flip every flag).
- Turn 2 changes part of what turn 1 did, so the final state is not a plain "replace everywhere".

## Reference solution
Turn 1:
1. bash: `find features -name '*.toml' | grep -v /frozen/ | xargs sed -i 's/^new_ui = false$/new_ui = true/'`
2. bash: `grep -rn '_ui\|beta' features`
Turn 2:
1. bash: `sed -i 's/^new_ui = true$/new_ui = false/' features/billing.toml features/payments.toml && sed -i 's/^beta_search = false$/beta_search = true/' features/search.toml`
2. bash: `grep -rn '_ui\|beta' features`
Final answers: DONE (turn 1: new_ui = true in the six services; turn 2: billing and payments back to false, search has beta_search = true).

## Why the answer is unique
Only the lines named by the two requests change, in the order they were asked; everything else is byte-identical to the fixture.

## Five alternative phrasings of the task
1. Enable new_ui across the services (not the frozen snapshot), then disable it for billing and payments and enable beta_search for search.
2. Flip new_ui to true in all feature files, afterwards revert billing and payments and switch on beta_search in search.
3. new_ui = true everywhere except frozen; then billing and payments false again, search gets beta_search.
4. Roll out the new UI flag to every service, then pull it back for the two finance services and give search the beta flag.
5. 把 features 里各服务的 new_ui 打开，之后 billing 和 payments 关回去，search 再开 beta_search
