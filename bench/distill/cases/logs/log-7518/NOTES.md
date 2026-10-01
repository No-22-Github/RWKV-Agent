## Traps
- TR-DUPROW: the export job retried, so Q-55201, Q-55219 and Q-55240 each appear as two identical lines (19 deferred rows). Counting rows gives 19; the README says a queue id identifies one message, so 16 distinct messages were deferred.

## Reference solution
1. Turn 1: read README.md (retried export, queue id = one message), read logs/delivery-events.jsonl, count distinct queue ids with event=deferred: 16 (19 rows, three duplicated). Answer: 16 messages.
2. Turn 2: of those, attempts >= 3: Q-55208, 55215, 55219, 55229, 55233, 55240, 55247, 55251, 55262, 55289 = 10. Answer: 10 messages.
3. Turn 3: drop the sandbox queue (Q-55215, dev@sandbox.heroncourier.cn): 9. Answer: 9 messages.
4. Turn 4: recipient domains among those nine: bramblehill.cn 5 (55229, 55233, 55240, 55251, 55262), tulipgrove.co.uk 2, heroncourier.cn 2. Answer: bramblehill.cn.
5. Turn 5: distinct queue ids with event=bounced: Q-55255, 55266, 55281, 55293 = 4. Answer: 4 messages.

## Why the answer is unique
The README makes the queue id the message identity, so the three duplicated lines collapse and every count is a distinct-id count; the decoy 19 is exactly the raw row count. The attempts field decides turn 2, the recipient suffix decides turn 3, and the domain split of the survivors (5-2-2) has a single winner. No duplicated pair belongs to the bounced set.
