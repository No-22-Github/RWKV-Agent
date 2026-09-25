## Traps
No traps. One search returns the Fernwharf reference page and the defaults table on
it answers the question.

## Reference solution
1. Search for the Fernwharf queue reference; the only result is
   docs.fernwharf.example/reference/queue-defaults.
2. Open that page: the table gives idle_expiry_days as 21, the middle column being
   the default, while dead_letter_expiry_days is 14 and max_message_kib is 512.

## Why the answer is unique
The page is Fernwharf's own reference and lists one default per setting. 14 is the
documented default of dead_letter_expiry_days, which bounds how long an undelivered
message is kept, and 512 bounds one message; the question asks how long a queue
itself survives without traffic, and only the idle_expiry_days row states 21. The
page also says polling does not count as activity, so a queue with an idle worker
still falls under that figure.

## Five alternative phrasings of the task
1. fernwharf queue default settings reference
2. how long does an idle fernwharf queue last
3. fernwharf idle_expiry_days default
4. fernwharf queue removed after days without messages
5. fernwharf task queue lifetime defaults table
