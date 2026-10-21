package eval

import "testing"

// work-v2 is frozen (docs/design/work-v3-tools.md §4.1): the App directory the
// 10-17 exam ran on recorded this hash in run.json. Any change to a work-v2
// tool's name, description, arguments or schema must fail here.
const workV2AppCatalogHash = "be0c317843959b20a82b016bd4eadf13ed17eca6a43ac9411ba94f9a7095fa35"

func TestWorkV2AppCatalogHashFrozen(t *testing.T) {
	if got := productCatalogHash(t.TempDir(), WorkV2ToolCatalogName); got != workV2AppCatalogHash {
		t.Fatalf("work-v2 App catalog hash drifted: got %s, want %s", got, workV2AppCatalogHash)
	}
}

// work-v3's hash as of the 10-21 behavior-only fixes (argument leniency,
// notes, Chinese errors): those changed what tools return, never what the
// model is told, so the hash is the one the 10-19/10-20 runs recorded. A
// description or argument change must fail here and bump the baseline.
const workV3AppCatalogHash = "70cca57d3cb83835f3e9f09426465e3bc453f165e0cd7bc435b32d3a393d70b0"

func TestWorkV3AppCatalogHashPinned(t *testing.T) {
	if got := productCatalogHash(t.TempDir(), WorkV3ToolCatalogName); got != workV3AppCatalogHash {
		t.Fatalf("work-v3 App catalog hash changed: got %s, want %s", got, workV3AppCatalogHash)
	}
}
