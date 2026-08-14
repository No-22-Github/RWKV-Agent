// Package netproxy configures the process-wide HTTP transport used by the
// application's remote providers.
package netproxy

import (
	"fmt"
	"net/http"
	"net/url"
	"os"
	"strings"
)

// Configure installs the macOS system proxy as a fallback for Go's default
// HTTP transport. Explicit proxy environment variables retain precedence.
// A missing or unsupported system proxy is deliberately not an error: direct
// networking remains the fallback.
func Configure() error {
	systemProxy, err := loadSystemProxy()
	if err != nil {
		return fmt.Errorf("load system proxy: %w", err)
	}
	if systemProxy == nil {
		return nil
	}

	base, ok := http.DefaultTransport.(*http.Transport)
	if !ok {
		return fmt.Errorf("http.DefaultTransport has unexpected type %T", http.DefaultTransport)
	}
	transport := base.Clone()
	transport.Proxy = func(request *http.Request) (*url.URL, error) {
		if proxyEnvironmentConfigured(request.URL.Scheme) {
			return http.ProxyFromEnvironment(request)
		}
		return systemProxy(request)
	}
	http.DefaultTransport = transport
	return nil
}

func proxyEnvironmentConfigured(scheme string) bool {
	var keys []string
	switch strings.ToLower(scheme) {
	case "http":
		keys = []string{"HTTP_PROXY", "http_proxy"}
	case "https":
		keys = []string{"HTTPS_PROXY", "https_proxy"}
	default:
		return false
	}
	for _, key := range keys {
		if strings.TrimSpace(os.Getenv(key)) != "" {
			return true
		}
	}
	return false
}
