## Traps
- None. `creel_bobbins` is written once, in `config/frame-settings.yaml`, and no other file in the workspace carries a competing figure.

## Reference solution
1. List the workspace: `README.md`, `config/frame-settings.yaml` and a note under `docs/`.
2. Read `config/frame-settings.yaml`, the settings file the README names: `creel_bobbins: 36`, so the frame threads 36 bobbins from the creel on each run.

## Why the answer is unique
The creel is threaded from its own settings file, and that file carries one count of bobbins. The other two keys describe different quantities (`twist_per_metre: 27` is a twist rate and `lay_hold_seconds: 55` a hold time), and the creel note covers where spare and worn bobbins go without giving a count, so neither can be read as the number on the creel. The answer is 36.
