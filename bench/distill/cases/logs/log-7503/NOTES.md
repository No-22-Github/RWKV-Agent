## Traps
- TR-MULTISRC: logs/batch-nightly.log alone suggests an EAST-2 network fault (the stock-sync session drops), which is the decoy "EAST-2". logs/ops-actions.csv shows CHG-2201 pushed rotated database credentials to the EAST-2 gateway at 01:02:11 and warned that the batch platform's credential copy was not synced — both failures start after that moment, so the shared root cause is the change, not the network.

## Reference solution
1. Turn 1: read logs/batch-nightly.log, find tasks that ended in a WARN 放弃/失败 line: stock-sync and payout. Answer: stock-sync、payout.
2. Turn 2: read logs/ops-actions.csv: CHG-2201 (credential rotation, 01:02:11) with the warning that the batch platform's copy was not updated; both tasks fail after it. Answer: CHG-2201.
3. Turn 3: count payout lines marked 重试: 3. Answer: 3 次.
4. Turn 4: the task that starts after payout gives up is digest; its last line is 01:31:44. Answer: 01:31:44.

## Why the answer is unique
The single-source decoy fails on timing: the ops log places the credential push at 01:02:11-01:02:16 and the first stock-sync failure at 01:03:03, and the README says the EAST-2 network is maintained by the site side with no fault recorded; only CHG-2201 links both failures. The retry count is read off the 重试 k/3 markers, and digest is the only task that both starts after payout's final line and completes, at 01:31:44.
