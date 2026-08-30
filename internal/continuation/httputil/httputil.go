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
	stopIndex := len(value)
	for _, stop := range stops {
		if stop == "" {
			continue
		}
		if index := strings.Index(value, stop); index >= 0 && index < stopIndex {
			stopIndex = index
		}
	}
	if stopIndex == len(value) {
		return value, false
	}
	return value[:stopIndex], true
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
