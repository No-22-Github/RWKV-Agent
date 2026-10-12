## Traps
- sqlite3 is not installed (`command not found`, exit 127); the query has to be redone with awk.
- TR-DECOY: the SQL filters status = 'completed' exactly; counting completed_partial rows too puts Braga on top.

## Reference solution
1. bash: the tool the user named -> exit 127 (`command not found`).
2. bash: `awk -F, '$3=="completed" {c[$2]++} END{for (k in c) print c[k], k}' data/visits.csv | sort -rn | head -1`
Final answer: The query returns Coimbra (sqlite3 is not available here, so I reproduced the query with awk: status exactly 'completed', most visits).

## Why the answer is unique
The script or query text in the fixture fixes the filter exactly; the fallback reproduces it with awk.

## Five alternative phrasings of the task
1. Use sqlite3 to execute queries/top_city.sql on the visits data and report the city it comes back with.
2. Which city does queries/top_city.sql return when run over data/visits.csv in sqlite3?
3. Please run the saved query top_city.sql with sqlite3 and give me the resulting city.
4. Execute the SQL file in queries/ through sqlite3 against the visits CSV; what city is the result?
5. sqlite3 < queries/top_city.sql on data/visits.csv: tell me the city in the output.
