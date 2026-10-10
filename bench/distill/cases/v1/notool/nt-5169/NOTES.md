## Traps
- TR-NOTOOLNEED: manifests/credential-field-cards.tsv and README.md are props. Whether the API credentials are provided is a field of the pod spec, so no file has to be read. The near-miss decoy `enableServiceLinks: false` is a real neighbouring field that gets confused with this one: it controls whether the environment variables for the cluster's services are injected, and the projected credentials are still provided.

## Reference solution
1. Answer from the pod spec: the field that decides whether the service account token is projected into the container is `automountServiceAccountToken`, and `false` turns it off.
2. Reply with the line `automountServiceAccountToken: false`.

## Why the answer is unique
The question asks for the setting under which the credentials are not provided at all, and `automountServiceAccountToken: false` is the field that governs exactly that projection. `enableServiceLinks: false` cannot be a reading of the question, because it only removes the environment variables describing the cluster's services: the credentials are still written into the container, which is what the question rules out.
