25 rows with distinct ISO dates; the header must not be sorted into the body.

Reference bash:

    { head -1 employees.csv; tail -n +2 employees.csv | sort -t, -k3,3; } > employees_sorted.csv

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
