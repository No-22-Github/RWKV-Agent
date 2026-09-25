## Traps
- TR-NOTOOLNEED: headers/download-header-cards.tsv and README.md are props. The disposition is a property of HTTP, so no file has to be opened to answer. The near-miss decoy `Content-Disposition: inline` is the default disposition and the opposite of the requirement: it invites the browser to show the body inside the tab.

## Reference solution
1. Answer from the header's own vocabulary: among the disposition types, the one that means "save this body to a file" is `attachment`.
2. Reply with the line `Content-Disposition: attachment`.

## Why the answer is unique
The question asks for the disposition under which the browser writes the body to a file, and `attachment` is the value that names that behaviour. `inline` is not a competing reading of the question: it is the value that asks for the body to be displayed in place, which is exactly what the question rules out. A filename parameter names the file rather than the behaviour, so it is the same answer with an extra parameter.
