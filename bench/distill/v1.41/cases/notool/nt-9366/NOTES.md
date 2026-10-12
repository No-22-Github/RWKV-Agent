## Traps
- TR-NOTOOLNEED: the user asks for a command to review and run later; running it, or listing/reading the files first, breaks the request.

## Reference solution
No tool call. Final answer: `rsync -av --dry-run ~/photos/ /mnt/backup/photos/`, then rerun without --dry-run.

## Why the answer is unique
The user said not to run anything; any tool call violates the request. The reply must contain the command (one of ['rsync']).

## Five alternative phrasings of the task
1. What command mirrors ~/photos to /mnt/backup/photos copying only changed files, with a preview mode? Only write it, don't run it.
2. Show me an incremental sync from ~/photos to /mnt/backup/photos, including a dry-run flag. No execution.
3. I want to back up ~/photos to /mnt/backup/photos and only transfer differences. Write the command with a preview option; I'll run it.
4. Command please (not executed): sync ~/photos into /mnt/backup/photos, updating only what changed, with a dry run first.
5. Give me a sync command for ~/photos -> /mnt/backup/photos that skips unchanged files and can preview first. Just the command.
