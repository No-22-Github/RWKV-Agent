// Package httputil holds the HTTP-client helpers shared by the continuation
// transports so their wire contracts cannot drift apart.
package httputil

import (
	"fmt"
	"net/url"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// ValidateEndpoint enforces the shared remote-endpoint contract: an absolute
// HTTP(S) URL without embedded credentials.
func ValidateEndpoint(endpoint string) error {
	parsed, err := url.Parse(endpoint)
	if err != nil || parsed.Scheme == "" || parsed.Host == "" {
		return fmt.Errorf("%w: endpoint must be an absolute HTTP(S) URL", continuation.ErrInvalidRequest)
	}
	if parsed.Scheme != "http" && parsed.Scheme != "https" {
		return fmt.Errorf("%w: endpoint scheme must be HTTP or HTTPS", continuation.ErrInvalidRequest)
	}
	if parsed.User != nil {
		return fmt.Errorf("%w: endpoint must not contain credentials", continuation.ErrInvalidRequest)
	}
	return nil
}

// TruncateAtStop cuts value at the earliest decoded-text stop sequence. Empty
// stops are skipped: they would otherwise match the whole value at offset 0.
func TruncateAtStop(value string, stops []string) (string, bool) {
	text, matched := TruncateAtStopMatch(value, stops)
	return text, matched != ""
}

// TruncateAtStopMatch is TruncateAtStop that also reports which stop sequence
// ended the text ("" when none matched).
func TruncateAtStopMatch(value string, stops []string) (string, string) {
	stopIndex := len(value)
	matched := ""
	for _, stop := range stops {
		if stop == "" {
			continue
		}
		if index := strings.Index(value, stop); index >= 0 && index < stopIndex {
			stopIndex = index
			matched = stop
		}
	}
	return value[:stopIndex], matched
}

// SafeResponseMessage condenses an error body for an error string: whitespace
// is collapsed, every configured secret is redacted, and the result is capped.
func SafeResponseMessage(body []byte, secrets ...string) string {
	const limit = 512
	value := strings.TrimSpace(string(body))
	value = strings.Join(strings.Fields(value), " ")
	for _, secret := range secrets {
		if secret != "" {
			value = strings.ReplaceAll(value, secret, "[REDACTED]")
		}
	}
	if len(value) > limit {
		value = value[:limit] + "..."
	}
	if value == "" {
		return "empty response"
	}
	return value
}

// SplitAtStop is the incremental form of TruncateAtStopMatch for streamed
// text: it returns the text safe to emit, the tail that may still grow into a
// stop, and the stop sequence that matched ("" when none did).
func SplitAtStop(value string, stops []string) (string, string, string) {
	stopIndex := len(value)
	matched := ""
	for _, stop := range stops {
		if index := strings.Index(value, stop); index >= 0 && index < stopIndex {
			stopIndex = index
			matched = stop
		}
	}
	if matched != "" {
		return value[:stopIndex], "", matched
	}
	tailBytes := 0
	for _, stop := range stops {
		limit := min(len(value), len(stop)-1)
		for length := 1; length <= limit; length++ {
			if length > tailBytes && strings.HasSuffix(value, stop[:length]) {
				tailBytes = length
			}
		}
	}
	safeBytes := len(value) - tailBytes
	return value[:safeBytes], value[safeBytes:], ""
}
