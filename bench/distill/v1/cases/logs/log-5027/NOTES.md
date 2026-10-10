## Traps
- TR-MULTISRC: the limit is nowhere in the feed journal. logs/telemetry-feed.log shows which batches were accepted and which were refused, and the limit itself is only in notes/hub-limits.md; the size of the first refused batch (138240) is a conspicuous substitute for it and is the wrong value.
- TR-SUPERSEDE: notes/hub-limits.md records three dated limits. The last one recorded (196608) is the newest and looks authoritative, but it was recorded on 25 August, a week after the refusals began, so the limit in force on 18 August is the earlier 131072.

## Reference solution
1. List the workspace: README.md, logs/telemetry-feed.log and notes/hub-limits.md.
2. Read README.md: the hub takes a batch within the payload limit it has set and turns a batch away over that limit, and the hub team records every change to the limit in notes/hub-limits.md.
3. Read logs/telemetry-feed.log. The last accepted batch is TW-7793 at 02:31:25 and the refusals run from TW-7794 at 02:41:27 on 18 August 2026, so the limit to record is the one in force on that date.
4. Read notes/hub-limits.md. The recorded changes are 2026-07-02 (131072), 2026-08-21 (262144) and 2026-08-25 (196608); the latest change on or before 18 August is the July one, so the limit in force was 131072 bytes.

## Why the answer is unique
The question asks for the limit in force when the refusals began, and the two files pin both halves of that: the feed journal dates the onset to 18 August 2026, and the change record is complete because the hub team records every change and the limit stays where the most recent change left it. The most recent change on or before 18 August is the 2 July change, which set the limit to 131072. The decoy 138240 is the body size of the first refused batch, a property of one batch rather than a limit and visible in the journal alone, and 196608 is the limit the record ended up at, which was recorded after the refusals started. With the onset date applied to the change record, the answer is 131072.

## Fixture notes
The feed journal holds accepted batches under the limit and refused ones over it, so its boundary brackets the limit without stating it, which is why the change record is needed. All stamps are UTC and every batch body is under the next recorded limit.
