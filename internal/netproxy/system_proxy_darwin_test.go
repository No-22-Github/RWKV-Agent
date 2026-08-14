//go:build darwin

package netproxy

import (
	"net/http"
	"testing"
)

func TestParseProxySettings(t *testing.T) {
	settings, err := parseProxySettings([]byte(`<dictionary> {
	ExceptionsList : <array> {
		0 : *.local
		1 : 169.254/16
	}
	ExcludeSimpleHostnames : 1
	HTTPEnable : 1
	HTTPPort : 8080
	HTTPProxy : 127.0.0.1
	HTTPSEnable : 1
	HTTPSPort : 8443
	HTTPSProxy : proxy.example
	SOCKSEnable : 0
}`))
	if err != nil {
		t.Fatal(err)
	}
	if got := settings.httpURL.String(); got != "http://127.0.0.1:8080" {
		t.Fatalf("HTTP proxy = %q", got)
	}
	if got := settings.httpsURL.String(); got != "http://proxy.example:8443" {
		t.Fatalf("HTTPS proxy = %q", got)
	}
	for _, host := range []string{"localhost", "127.0.0.1", "printer", "host.local", "169.254.2.3"} {
		if !settings.bypasses(host) {
			t.Errorf("expected %q to bypass the proxy", host)
		}
	}
	if settings.bypasses("api.search.brave.com") {
		t.Error("Brave Search must use the proxy")
	}
}

func TestConfigureUsesSystemProxyWithoutEnvironment(t *testing.T) {
	for _, key := range []string{
		"HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy",
		"ALL_PROXY", "all_proxy", "NO_PROXY", "no_proxy",
	} {
		t.Setenv(key, "")
	}
	systemProxy, err := loadSystemProxy()
	if err != nil {
		t.Fatal(err)
	}
	if systemProxy == nil {
		t.Skip("macOS has no explicit system proxy configured")
	}
	originalTransport := http.DefaultTransport
	t.Cleanup(func() { http.DefaultTransport = originalTransport })
	if err := Configure(); err != nil {
		t.Fatal(err)
	}
	request, err := http.NewRequest(http.MethodGet, "https://api.search.brave.com", nil)
	if err != nil {
		t.Fatal(err)
	}
	transport, ok := http.DefaultTransport.(*http.Transport)
	if !ok {
		t.Fatalf("default transport type = %T", http.DefaultTransport)
	}
	got, err := transport.Proxy(request)
	if err != nil {
		t.Fatal(err)
	}
	want, err := systemProxy(request)
	if err != nil {
		t.Fatal(err)
	}
	if got == nil || want == nil || got.String() != want.String() {
		t.Fatalf("proxy = %v, want %v", got, want)
	}
}
