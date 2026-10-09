5xx counts {'cart': 23, 'auth': 25, 'pricing': 53, 'inventory': 21, 'search': 36}. Answer pricing / Hana Kobayashi.

Reference bash:

    for f in services/*/logs/app.log; do echo "$(grep -c 'status=5' $f) $f"; done | sort -rn | head -1
    cat services/pricing/OWNERS

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
