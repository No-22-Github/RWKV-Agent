## Traps
- TR-PRECEDENCE: max_stay_min is defined in the common config (120) and again
  in the pool area file (90); the area file wins. Reading only the common file
  reports 120.

## Reference solution
1. Read README.md: which file belongs to the pool area and the area-over-common
   order.
2. Read config/spring-pool.yaml: max_stay_min is 90.
3. Read config/spring-common.yaml: the common 120 is overridden.

## Why the answer is unique
The README maps the pool area to spring-pool.yaml and states the area file wins
on same-name keys, so between 120 and 90 exactly one is effective for the pool
area. The question asks about the pool area specifically, and no file supports
120 as the area's effective value, leaving 90.
