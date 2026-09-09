package bfcl

import (
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
)

// TestAnchorsShareWireConstants locks the P5 convergence: the BFCL benchmark
// tiers read the same anchor bytes as the product harness, so a change to a
// measured prefill cannot land in only one of them.
func TestAnchorsShareWireConstants(t *testing.T) {
	t.Parallel()
	if XMLAnchor != wire.EnvelopePrefix+wire.CallBodyAnchor {
		t.Fatalf("XMLAnchor = %q", XMLAnchor)
	}
	if xmlClosedThinkPrefix != wire.FakeThinkClosedPrefix {
		t.Fatalf("xmlClosedThinkPrefix = %q", xmlClosedThinkPrefix)
	}
	if MultiTurnAnchorObject.Prefill() != wire.DeepFencePrefix {
		t.Fatalf("object prefill = %q", MultiTurnAnchorObject.Prefill())
	}
	if MultiTurnAnchorFence.Prefill() != wire.FencePrefix {
		t.Fatalf("fence prefill = %q", MultiTurnAnchorFence.Prefill())
	}
	if MultiTurnAnchorArray.Prefill() != wire.FencePrefix+"[" {
		t.Fatalf("array prefill = %q", MultiTurnAnchorArray.Prefill())
	}
	if prefillAnchor("parallel") != wire.ArrayCallAnchor {
		t.Fatalf("parallel anchor = %q", prefillAnchor("parallel"))
	}
	if prefillAnchor("simple_python") != wire.CallBodyAnchor {
		t.Fatalf("single anchor = %q", prefillAnchor("simple_python"))
	}
}
