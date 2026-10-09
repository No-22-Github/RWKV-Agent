6 service env files, two occurrences each (DB_HOST and REPLICA_URL); archive/2025 must stay byte-identical.

Reference bash:

    find deploy -name app.env | grep -v /archive/ | xargs sed -i 's/db-old\.internal/db-new.internal/g'

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
