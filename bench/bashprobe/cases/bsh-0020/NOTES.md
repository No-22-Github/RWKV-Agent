Fixed clock is 2026-09-16, so 明天 = 2026-09-17 (多云 18~25). Probes the 2026-10-09 failure where the model kept searching after get_weather instead of producing the artifact.

Reference bash:

    echo '2026-09-17 杭州 多云 18~25°C' >> notes/daily.md

<!-- BASHPROBE-CANARY-7d41c0e9 : never enters training corpora -->
