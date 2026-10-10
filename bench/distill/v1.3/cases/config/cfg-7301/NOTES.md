## Traps
- TR-NEARNAME: burst_count appears in two sections; preview.burst_count (2)
  belongs to the framing preview path and must stay untouched, while
  capture.burst_count (5) is the main recording path the request is about.

## Reference solution
1. Read README.md: capture is the main recording path, preview is the framing
   preview on the operator's monitor.
2. Read config/capture.yaml.
3. Change capture.burst_count from 5 to 8 and save the file.

## Why the answer is unique
The request names the main recording path, and the README maps that to the
capture section only; the preview section keeps bitrate_mbps 12, burst_count 2
and scale 0.5. The equals check on config/capture.yaml compares the whole
file, so a second edit (preview included) or a reformat of untouched lines
fails as well, which is what keeps the change minimal.
