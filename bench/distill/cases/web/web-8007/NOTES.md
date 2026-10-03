## Traps
- TR-WEBSTALE: the first hit is a 2025 forum reply calling E4127 a network timeout (that is E4126 in the official reference). The official error reference says E4127 means the lockfile was written by a newer Halyard version.

## Reference solution
1. Search Halyard E4127: forum thread and the official error reference.
2. Fetch https://halyard.sh/docs/errors.
Final answer, 1-2 sentences: E4127 means the lockfile was written by a newer Halyard than the one CI runs; upgrade Halyard in CI or regenerate the lockfile with the CI version (official error reference). Criteria: contains "newer" and lockfile; does not present it as a network timeout.

## Why the answer is unique
The official reference defines each code; the forum reply conflates E4127 with E4126.

## Changelog
- v2: max_output_chars raised to 600, the §4.2 limit; the pilot answer (490 chars) was correct and within the spec limit but over the stricter limit this case had set.

## Five alternative phrasings of the task
1. Halyard error E4127
2. halyard E4127 meaning
3. Halyard CLI error codes
4. halyard lockfile E4127
5. what is halyard error E4127
