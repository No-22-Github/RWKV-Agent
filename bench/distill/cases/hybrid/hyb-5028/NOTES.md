## Traps
- TR-AMBIG: the first request asks for the last reading from Tank 2, and two dairies run
  a tank with that number. Ruscombe's last reading, on 25 September, is 4020; Tilshead's,
  on 29 September, is 3980. The sheet cannot say which dairy the closing sheet covers, so
  the assistant has to ask.

## Reference solution
1. list_files: the workspace holds readings/tank-2-2026-09.csv and README.md.
2. read_file readings/tank-2-2026-09.csv: rows for Tank 2 sit under two dairies, so the
   request is not yet settled and the assistant asks which tank is meant.
3. Turn 2 fixes the Ruscombe tank. Its readings run 3180, 3540, 3875 and 4020 on 25
   September, so the last reading is 4020.

## Why the answer is unique
After the clarification one tank is in scope. Each row states the date the reading was
taken, so the last reading is the one with the latest date among that tank's rows:
Ruscombe's final row is 25 September with 4020. The decoy 3980 is Tilshead's last reading,
taken four days later on the other dairy's tank; it is a real reading, but the sheet was
settled on the Ruscombe tank before the latest date was picked.

## Five alternative phrasings of the task
1. cogdean dairies tank 2 readings september
2. last tank 2 reading in september
3. ruscombe and tilshead tank 2 readings
4. cogdean dairies storage tank readings
5. tank 2 final reading september
