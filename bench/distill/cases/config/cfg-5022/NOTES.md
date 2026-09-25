## Traps
- None. `blanket_wash_after_sheets` is written once, in `config/press-run.toml`, and no other file in the workspace carries a competing figure.

## Reference solution
1. List the workspace: `README.md`, `config/press-run.toml` and a note under `docs/`.
2. Read `config/press-run.toml`, the file the README names: `blanket_wash_after_sheets = 288`, so the press prints 288 sheets between blanket washes.

## Why the answer is unique
The wash interval sits in one key of one file, and the file is the only source the press reads. The other two keys in it measure different things (`ink_duct_cycles = 14` counts duct cycles, `chill_roll_temp_c = 11` is a temperature), and the press hall note covers deliveries and cleaning cloths without mentioning the press run. Reading either of the other figures as the sheet count answers a question nobody asked. The answer is 288.
