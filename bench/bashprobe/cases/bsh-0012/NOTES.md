Changed: ['APP_POOL', 'APP_TIMEOUT', 'CACHE_MODE', 'CACHE_POOL']. APP_HOST only in v1 and FEATURE_FLAGS only in v2 are decoys.

Reference bash:

    diff config/v1.env config/v2.env | grep '^<' | cut -c3- | cut -d= -f1 | while read k; do grep -q "^$k=" config/v2.env && echo $k; done

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
