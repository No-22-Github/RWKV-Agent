## Traps
- TR-NOTOOLNEED: deps/cache-mount-cards.tsv, README.md and notes/runner-notes.txt are props. How a build step mounts a cache is a property of the container builder, so nothing on disk has to be read. The near-miss decoy `--mount=type=bind,...` exposes a directory from the build inputs instead of a cache: nothing is written back to it between builds, the wheels are downloaded again, and the directory it exposes belongs to the image inputs.

## Reference solution
1. Answer from the builder's own vocabulary: a directory the installer reads and writes that must survive between builds and stay out of the layers is mounted with `--mount=type=cache`.
2. Reply with the build step line `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt`.

## Why the answer is unique
The question asks for a mount that is reused by the next build and never becomes part of a layer, and `type=cache` is the mount type with exactly those two properties. `type=bind` cannot be a reading of the question: a bind mount makes a build input visible to the step, so the directory the installer writes is either discarded or part of the image inputs, and it is never handed back to the next build as a cache.
