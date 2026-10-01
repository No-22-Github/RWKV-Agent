## Traps
- TR-PRECEDENCE: alert_delay_s is defined in both layers; the site YAML (20)
  overrides the region baseline (30). Reading only the baseline gives 30.
- TR-DECOY: the site YAML carries a commented-out line about a retired trial
  value 120, which looks like a recent operating figure. Neither 30 nor 120 is
  effective.

## Reference solution
1. Read README.md: the two config layers and the site-over-baseline order.
2. Read config/pump-station.yaml: the active line alert_delay_s: 20 is effective;
   the commented line about 120 is a remark, not a setting.
3. Read config/region-baseline.json: its 30 loses to the site value.

## Why the answer is unique
The README fixes the layer order and says hash lines in the site file are
remarks, so the commented 120 is out by the file's own convention, and the
baseline 30 loses to the site value by the stated order. Only the active site
line survives both rules, giving 20; no reading makes 30 or 120 effective.
