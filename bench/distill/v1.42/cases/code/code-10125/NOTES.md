## Traps
- TR-READONLY: generated/pb stay unchanged per src/handlers/README.md.
- catalog.Printf( ends with log.Printf(; a pattern without a word boundary rewrites it to catalslog.Info(.
- 5 files change; 2 stay byte-identical.

## Reference solution
1. bash: `find src/handlers -name '*.go' -not -path '*/generated/*' | xargs sed -i -E 's/\blog\.Printf\(/slog.Info(/g'`
2. bash: `grep -rnF 'slog.Info(' src/handlers`
Final answer: Done across the in-scope files; the protected folder and the look-alike text are unchanged. Checked with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
