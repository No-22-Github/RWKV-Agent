## Traps
- TR-READONLY: app/compat/shim.py keeps old_logger. TR-DECOY: `old_logger_test_helper` (db/session.py) contains old_logger as a prefix and must not be renamed.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find app -name '*.py' | grep -v /compat/ | xargs sed -i '/old_logger_test_helper/!s/old_logger/new_logger/g'`
2. bash: `grep -rn logger app`
Final answer: DONE (api, db, cache, nightly, weekly use new_logger).
Turn 2:
1. bash: `sed -i 's/new_logger/old_logger/g' app/jobs/nightly.py app/jobs/weekly.py`
2. bash: `grep -rn logger app`
Final answer: DONE (nightly and weekly use old_logger again, api/db/cache use new_logger).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. Rename the logger identifier old_logger to new_logger across app (not compat, not the test helper), then revert the nightly and weekly jobs.
2. Switch all modules to new_logger except the compat shim; the two job files go back to old_logger.
3. old_logger -> new_logger everywhere in app except compat; then undo it in jobs/nightly.py and jobs/weekly.py.
4. Replace the old logger name in the app modules, keeping old_logger_test_helper, then restore it in the jobs.
5. 把 app 里的 old_logger 改名为 new_logger，之后 nightly 和 weekly 两个任务改回去
