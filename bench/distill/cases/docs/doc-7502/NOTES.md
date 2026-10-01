## Traps
- TR-DECOY: docs/CHANGELOG.txt keeps a v2.6.2 billing-export hotfix (BC-117) whose wording mirrors the v2.7.0 billing entry. A careless pass reports `BC-117`.

## Reference solution
1. List docs/ to find the changelog.
2. Read README.md for the entry format.
3. Read docs/CHANGELOG.txt, take the first version block down to the next version header, and answer.

## Why the answer is unique
BC-117 belongs to the v2.6.2 block that follows the v2.7.0 header, and the changelog appends newest first, so the newest release is exactly the lines after the first header. The reverted v2.6.0 draft never shipped, and no other card id appears inside the v2.7.0 block.
