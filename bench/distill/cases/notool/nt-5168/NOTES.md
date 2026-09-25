## Traps
- TR-NOTOOLNEED: manifests/pull-policy-cards.tsv and README.md are props. When an image is fetched again is a property of the pod spec, so nothing has to be read before replying. The near-miss decoy `imagePullPolicy: IfNotPresent` is the default that trusts a locally held copy, so with a tag that is overwritten in place the node keeps running the previous build.

## Reference solution
1. Answer from the pod spec: the field that decides when the image is fetched is `imagePullPolicy`, and the value that always asks the registry is `Always`.
2. Reply with the line `imagePullPolicy: Always`.

## Why the answer is unique
The question asks for the setting under which the image is fetched again at every container start, and among the three values of `imagePullPolicy` only `Always` asks the registry regardless of what the node holds. `IfNotPresent` cannot be a reading of the question: it is the value that skips the registry when a copy is present, so the overwritten tag is never noticed.
