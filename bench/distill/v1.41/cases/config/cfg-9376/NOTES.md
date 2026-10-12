## Traps
- TR-DECOY: [pr] has test_shards = 4; pipeline.toml.sample has 3 for nightly.

## Reference solution
1. read_file ci/pipeline.toml
Final answer: The nightly pipeline uses 8 test shards (PR runs use 4).

## Why the answer is unique
The user names ci/pipeline.toml; only its live line holds the answer. [pr] uses 4 shards and the .sample file has other numbers.
Why bash is not the tool here: one named file and one fact, read_file is the direct read. Bash is offered, but a shell call would be wasted effort.

## Five alternative phrasings of the task
1. How many shards does the nightly run split tests into according to ci/pipeline.toml?
2. ci/pipeline.toml: what is test_shards under [nightly]?
3. What's the nightly test shard count in ci/pipeline.toml?
4. Look at ci/pipeline.toml and tell me the number of test shards for the nightly job.
5. Nightly CI parallelism (test_shards) per ci/pipeline.toml?
