600 lines; counts are all distinct so the order is unique. Expected file:

status,count
200,300
304,120
404,70
201,51
500,41
502,18

Reference bash:

    mkdir -p report && { echo status,count; awk '{print $4}' logs/requests.log | sort | uniq -c | sort -rn | awk '{print $2","$1}'; } > report/status_counts.csv

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
