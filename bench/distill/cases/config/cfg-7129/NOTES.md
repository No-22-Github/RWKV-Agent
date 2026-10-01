## Traps
- TR-PRECEDENCE: the prompt hands over deploy/global.env, where MAX_UPLOAD_MB
  reads 50; the service env deploy/harvest-api.env overrides it with 200.
  Stopping at the named file reports 50.

## Reference solution
1. Read deploy/global.env (path given in the prompt): MAX_UPLOAD_MB is 50 there,
   but this is the platform default layer.
2. Read README.md: keys set in a service env override the platform global env.
3. Read deploy/harvest-api.env: MAX_UPLOAD_MB is 200 and wins.

## Why the answer is unique
The README fixes the direction (service env over global env) and both layers
carry the key, so exactly one figure is effective for harvest-api. The 50 in the
global file is the layer that loses; nothing in the workspace supports 50 as the
service's effective cap, leaving 200.
