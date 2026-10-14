## Traps
No traps. One search returns the Grimsdale reference page and the defaults table on
it answers the question.

## Reference solution
1. Search for the Grimsdale artifact reference; the only result is
   docs.grimsdale.example/reference/artifact-retention.
2. Open that page: the table gives build_log_keep_days as 27, while
   binary_keep_days is 90, upload_timeout_seconds is 45 and max_artifact_mib is 512.

## Why the answer is unique
The page is Grimsdale's own reference and lists one default per setting. 90 is the
window for binaries, a different artifact written by the same build; 45 bounds one
upload request and 512 caps one artifact. The question asks how long a build log
itself stays available, and only the build_log_keep_days row states 27; the page
adds that no second copy is written, so nothing survives past that window.

## Five alternative phrasings of the task
1. grimsdale artifact retention defaults
2. how long does grimsdale keep build logs
3. grimsdale build_log_keep_days default
4. grimsdale reference artifact retention table
5. grimsdale build log window after a build finishes
