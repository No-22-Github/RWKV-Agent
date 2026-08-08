//go:build !chatcompletions

package chatcompletions

import (
	"errors"
	"strings"
	"testing"
)

func TestNewReportsOptionalBuildRequirement(t *testing.T) {
	t.Parallel()
	client, err := New(Config{
		Endpoint: "https://api.example.test/v1/chat/completions",
		Model:    "example-model",
	})
	if client != nil || !errors.Is(err, ErrNotBuilt) ||
		!strings.Contains(err.Error(), "-tags chatcompletions") {
		t.Fatalf("client = %v, error = %v", client, err)
	}
}
