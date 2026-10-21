package wire

import "testing"

// presetHashes pins the wire hash of every registered preset. The hash covers
// the model-facing bytes; the preset name is not part of it, so renaming a
// preset must not move a single value. A mismatch means the code changed what
// the model sees — investigate the cause, do not update the expectation.
var presetHashes = map[string]string{
	"bfcl-md-v1":         "403ef7f1fec374d615c171a1a83521e5942afe45c83ec49a6993eefb6cec0abb",
	"bfcl-xml-v1":        "fe195e3f56e8f6cfb0b2f1b98888c46a4f8854ecd4b34378f47be53cc548f295",
	"default":            "2b9adc0fe4bf2d1104e0639910c4bde47f1579f54586f8e41d147acdbd43573b",
	"g1k":                "993fd7b0a09d3a6b90e0dc674857c22122d1d024414660e2b1b395d68f90ecc7",
	"g1k-think":          "449ef2fa7eb0d018d1abdb0e91e96ef2bfb1d4476d41e032f49fe9585b7a2133",
	"md-fakethink-v1":    "b52b50bc2dfbc5974e6f3ab432f471c4efbda2c4c5a97c2da7ce0e1c6b4c8fdb",
	"md-fence-v1":        "6d77d4e38986c9b454e625a936a7d489ce4a4d095aaa67114b639e36dd5ac617",
	"md-v1":              "a0db4ae8edb6e552d04322de218e825daaba18ae2ad52fef9ea71addc16a9e75",
	"native-v1":          "2119701cd3f2d5bf2d110c02020335323f1fa59a3825d5cecd35995b7dc2447b",
	"primitive-v1":       "a133b226bfd6c362e4a921b0ea21a18fde096bdddc79a5a486a3c4ecf8fdc623",
	"xml-progressive-v1": "fe195e3f56e8f6cfb0b2f1b98888c46a4f8854ecd4b34378f47be53cc548f295",
	"xml-route-v1":       "44cf37f2faeb4a5d40c1bce745079aaae4789530ce2e1287ea8f05a7e7e8c4d7",
	"xml-v1":             "2b9adc0fe4bf2d1104e0639910c4bde47f1579f54586f8e41d147acdbd43573b",
}

func TestPresetHashesArePinned(t *testing.T) {
	for name, want := range presetHashes {
		spec, ok := Lookup(name)
		if !ok {
			t.Errorf("preset %q is not registered", name)
			continue
		}
		if got := spec.Hash(); got != want {
			t.Errorf("preset %q hash = %s, want %s (what the model sees changed)", name, got, want)
		}
	}
	for _, name := range Names() {
		if _, pinned := presetHashes[name]; !pinned {
			spec, _ := Lookup(name)
			t.Errorf("preset %q is registered but not pinned; add %q: %q", name, name, spec.Hash())
		}
	}
}
