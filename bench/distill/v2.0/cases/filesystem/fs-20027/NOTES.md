## Traps
- TR-DECOY: a similar name must survive.

## Reference solution
bash `rm tmp/*.log`，再 ls 核对只剩 keep.txt；回答删了 3 个。

## Why the answer is unique
bash is offered and works in the sandbox, so the files must end up exactly as expect.files says (a reply claiming it without the change fails, and so does leaving the files alone).
