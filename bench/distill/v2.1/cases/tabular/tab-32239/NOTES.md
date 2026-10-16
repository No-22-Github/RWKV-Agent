## Traps
- TR-DECOY: an exact-case comparison reports extra non-subscribers.

## Reference solution
1. lowercase both, sort, comm -23.
Reference commands (replayed in the sandbox): tail -n +2 crm/members.csv | cut -d, -f1 | tr A-Z a-z | sort > /tmp/a.txt; tail -n +2 crm/newsletter.csv | cut -d, -f1 | tr A-Z a-z | sort > /tmp/b.txt; comm -23 /tmp/a.txt /tmp/b.txt > /tmp/o.txt; cat /tmp/o.txt; wc -l < /tmp/o.txt
Final answer: turn 1 -> 5 user1129@mail.example user1174@mail.example user1413@mail.example user2027@mail.example user2128@mail.example

## Why the answer is unique
Case-insensitive set difference.
