## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: A hard link is another name for the same inode so the data survives deleting the original name; a symlink stores a path and dangles/breaks if the target is removed.

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['inode', 'pointer', 'dangling', 'broken', 'path', 'shortcut'].

## Five alternative phrasings of the task
1. Explain ln versus ln -s: hard links vs symlinks.
2. If I delete the original file, which kind of link still works?
3. Hard link or soft link: how do they differ internally?
4. What is an inode and how does it relate to hard links?
5. Why can't hard links point to directories or across filesystems while symlinks can?
