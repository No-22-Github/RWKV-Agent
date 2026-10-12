## Traps
- TR-READONLY: etc/readonly keeps .cfg throughout. TR-DECOY: old.cfg.bak is a backup, not a .cfg file.
- Turn 3 undoes both earlier turns: no .conf file remains and every original .cfg path is back with its content.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere; turn 3 undoes the whole change.

## Reference solution
Turn 1:
1. bash: `for f in $(find etc -name '*.cfg' | grep -v /readonly/); do mv "$f" "${f%.cfg}.conf"; done`
2. bash: `find etc -type f`
Final answer: DONE (seven files renamed to .conf, readonly untouched).
Turn 2:
1. bash: `for f in etc/legacy/*.conf; do mv "$f" "${f%.conf}.cfg"; done`
2. bash: `find etc -type f`
Final answer: DONE (legacy files are .cfg again).
Turn 3:
1. bash: `for f in $(find etc -name '*.conf'); do mv "$f" "${f%.conf}.cfg"; done`
2. bash: `find etc -type f`
Final answer: DONE (all files are .cfg again).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. Rename .cfg to .conf under etc (not readonly), restore legacy, then roll back the entire rename.
2. Change the config extension to .conf, put legacy back to .cfg, finally cancel the change completely.
3. .cfg -> .conf except readonly; legacy returns; then everything goes back to .cfg.
4. Do the extension migration, partially revert legacy, then undo the rest as well.
5. 把 etc 里的 .cfg 改成 .conf，legacy 改回去，最后整体撤销，全部恢复 .cfg
