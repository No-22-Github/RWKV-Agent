## Traps
- TR-EARLYHIT: the first result, docs.saltmarsh.example/reference/queues, already states the default for standard queues, so one search is enough; docs.saltmarsh.example/reference/batch-queues is a second page about batch queues whose 600-second default is the decoy for anything but a batch queue.

## Reference solution
1. Search once for the Saltmarsh queue settings: the first result is the standard-queue reference page, whose snippet gives the 90-second visibility timeout, and the batch-queue page is listed with it.
2. Open docs.saltmarsh.example/reference/queues and confirm "defaults to 90 seconds for standard queues"; answer 90.

## Why the answer is unique
The question names a standard queue, and the two pages are separate references: the standard-queue page states 90 seconds, while the batch-queue page states its own 600 seconds and labels itself as the reference for batch queues. 600 therefore describes a different queue type, and the question never asks about batch queues. 43200 is the ceiling a queue can be raised to, not the default, and 5 is the delivery-attempt default.

## Five alternative phrasings of the task
Every query below carries the fixture keyword saltmarsh, so each one is answered by a fixture entry.
1. saltmarsh standard queue visibility timeout default
2. saltmarsh queue settings reference
3. saltmarsh how long until a message is redelivered
4. saltmarsh visibility timeout seconds
5. saltmarsh message visibility window
