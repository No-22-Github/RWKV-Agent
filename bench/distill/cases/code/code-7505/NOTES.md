## Traps
- TR-DECOY: core/sink.py 的注释里留着旧队列 kafka://events.gulan.internal/legacy，粗读会当成正常出口。 A careless pass reports `kafka://events.gulan.internal/legacy`.

## Reference solution
1. Read core/loader.py for the default sink and the retry loop.
2. Read core/sink.py for the dead-letter target.
3. Explain the happy path, the trigger and the fallback in one paragraph.

## Why the answer is unique
The legacy queue exists only as a commented line in sink.py and no code references it, so the live sink is kafka://events.gulan.internal/main. The loop retries on TimeoutError up to MAX_ATTEMPTS and then delivers to DEAD_LETTER, the s3://gulan-deadletter/loader bucket, which pins all three behaviors.
