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
